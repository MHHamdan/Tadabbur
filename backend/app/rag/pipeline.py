"""
RAG Pipeline for grounded Quranic Q&A.

CRITICAL SAFETY RULES:
1. NEVER invent tafseer - LLM may ONLY summarize retrieved evidence
2. Every paragraph MUST include at least one citation
3. Citations MUST be validated against retrieved chunks
4. If evidence is insufficient, return safe refusal
5. For fiqh/rulings: informational summary only, no fatwa language

LANGUAGE POLICY:
================
RAG reasoning is ONLY performed in Arabic (ar) and English (en):
- Semantic search embeddings exist only for ar/en tafseer content
- LLM synthesis uses ar/en source material

Other languages (Urdu, Indonesian, etc.) are DISPLAY-ONLY:
- Verse translations come from the translations table
- NO tafseer retrieval or RAG reasoning in these languages
- Use the /translations endpoint for display languages

RAG SCOPE FREEZE (PROHIBITED BEHAVIORS)
=======================================
This pipeline MUST NOT be extended to:

1. GENERATE explanations beyond retrieved evidence
   - No "creative" interpretation
   - No inference beyond what sources explicitly state
   - No filling gaps with general knowledge

2. TRANSLATE tafseer dynamically
   - No LLM-based translation of Arabic tafseer to English
   - No translating answers to display-only languages
   - Translations must come from pre-verified translated sources only

3. REASON over display-only languages
   - No RAG retrieval in Urdu, Indonesian, Turkish, etc.
   - No embedding search in non-AR/EN content
   - Display-only languages are served from translations table ONLY

4. PROVIDE religious rulings (fatwa)
   - Fiqh content is INFORMATIONAL only
   - Must include disclaimer to consult scholars
   - No personalized religious advice

5. SYNTHESIZE across conflicting sources without disclosure
   - Must indicate when scholars disagree
   - Must not present disputed views as consensus

Any modification to these rules requires:
- Update to this docstring
- Update to app/core/acceptance.py
- Full test suite re-run
- Security review
"""
import re
import time
import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.rag.types import (
    QueryIntent,
    RetrievedChunk,
    Citation,
    GroundedResponse,
    SAFE_REFUSAL_INSUFFICIENT,
    SAFE_REFUSAL_NO_SOURCES,
    SAFE_REFUSAL_FIQH,
    RAG_SUPPORTED_LANGUAGES,
)
from app.rag.retrieval import HybridRetriever
from app.rag.prompts import GROUNDED_SYSTEM_PROMPT, build_user_prompt
from app.rag.query_expander import expand_query, ExpandedQuery
from app.rag.confidence import confidence_scorer, get_confidence_message, ConfidenceBreakdown
from app.validators.citation_validator import CitationValidator
from app.rag.llm_provider import get_llm, LLMProvider, BaseLLM

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG pipeline for grounded Quranic Q&A.

    Flow:
    1. Classify query intent
    2. Expand query with Islamic terminology
    3. Retrieve relevant chunks (vector + keyword)
    4. Build grounded context
    5. Generate response with strict grounding rules
    6. Validate all citations
    7. Return response with citations or safe refusal
    """

    def __init__(
        self,
        session: AsyncSession,
        llm_provider: LLMProvider = None,
    ):
        self.session = session
        self.retriever = HybridRetriever(session)
        self.validator = CitationValidator(session)

        # Initialize LLM provider (defaults to configured provider)
        if llm_provider is None:
            llm_provider = LLMProvider(settings.llm_provider)

        try:
            self.llm = get_llm(provider=llm_provider)
            self.llm_provider = llm_provider
            logger.info(f"RAG Pipeline initialized with {llm_provider.value} provider")
        except Exception as e:
            logger.warning(f"Failed to initialize {llm_provider}: {e}")
            self.llm = None
            self.llm_provider = None

    async def query(
        self,
        question: str,
        language: str = "en",
        include_scholarly_debate: bool = True,
        preferred_sources: List[str] = None,
        max_sources: int = 5,
    ) -> GroundedResponse:
        """
        Process a question and return a grounded response.

        Args:
            question: The user's question
            language: Response language (ar/en ONLY - see LANGUAGE POLICY)
            include_scholarly_debate: Include differing scholarly views
            preferred_sources: List of preferred tafseer source IDs
            max_sources: Maximum number of sources to retrieve

        Returns:
            GroundedResponse with answer, citations, and metadata

        Note:
            RAG reasoning is only supported in Arabic (ar) and English (en).
            Other languages will be coerced to English. For display-only
            translations in other languages, use the /translations endpoint.
        """
        # Validate language - RAG only supports ar/en
        if language not in RAG_SUPPORTED_LANGUAGES:
            language = "en"  # Coerce to English (validation logged in retriever)

        # 1. Classify intent
        intent = await self._classify_intent(question)

        # 2. Expand query with Islamic terminology
        expanded = expand_query(question)
        search_query = expanded.combined if expanded.expansion_applied else question

        # 3. Retrieve relevant chunks using expanded query
        chunks = await self.retriever.retrieve(
            query=search_query,
            language=language,
            intent=intent,
            preferred_sources=preferred_sources or [],
            top_k=max_sources * 2,  # Retrieve more, then filter
        )

        # 4. Rerank chunks based on relevance and source reliability
        chunks = self._rerank_chunks(chunks, question, max_sources)

        # 5. Check if we have enough evidence
        if not chunks:
            return GroundedResponse(
                answer=SAFE_REFUSAL_NO_SOURCES,
                citations=[],
                confidence=0.0,
                intent=intent.value,
                warnings=["No relevant sources found"],
                query_expansion=expanded.expansion_applied if expanded.expansion_applied else None,
                api_version=settings.api_version,
            )

        # 6. Build context from retrieved chunks
        context = self._build_context(chunks, language)

        # 7. Generate grounded response
        raw_response, llm_latency_ms = await self._generate_response(
            question=question,
            context=context,
            intent=intent,
            language=language,
            include_scholarly_debate=include_scholarly_debate,
        )

        # 8. Parse and validate response with enhanced confidence scoring
        chunk_ids = [c.chunk_id for c in chunks]
        validated = await self._validate_and_parse_response(
            raw_response=raw_response,
            chunks=chunks,
            chunk_ids=chunk_ids,
            intent=intent,
            query_expansion=expanded,
        )

        # Add LLM latency to processing time
        validated.processing_time_ms = llm_latency_ms

        return validated

    def _rerank_chunks(
        self,
        chunks: List[RetrievedChunk],
        original_query: str,
        max_results: int,
    ) -> List[RetrievedChunk]:
        """
        Rerank retrieved chunks based on multiple factors.

        Factors:
        1. Relevance score (from retrieval)
        2. Source reliability
        3. Query term coverage
        4. Recency/primary source preference
        """
        if not chunks:
            return []

        query_terms = set(original_query.lower().split())

        scored_chunks = []
        for chunk in chunks:
            # Base score from retrieval
            score = chunk.relevance_score

            # Boost for primary sources
            if getattr(chunk, 'is_primary_source', False):
                score += 0.1

            # Boost for high reliability sources
            reliability = getattr(chunk, 'source_reliability', 0.8)
            score += reliability * 0.1

            # Boost for query term overlap
            content = (chunk.content_en or chunk.content_ar or "").lower()
            content_terms = set(content.split())
            overlap = len(query_terms & content_terms)
            if query_terms:
                overlap_ratio = overlap / len(query_terms)
                score += overlap_ratio * 0.15

            scored_chunks.append((score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Return top results
        return [chunk for score, chunk in scored_chunks[:max_results]]

    async def _classify_intent(self, question: str) -> QueryIntent:
        """
        Classify the query intent using rule-based matching first,
        then LLM if needed.
        """
        q_lower = question.lower()

        # Rule-based classification
        if any(word in q_lower for word in ["meaning", "tafseer", "explain", "معنى", "تفسير"]):
            return QueryIntent.VERSE_MEANING

        if any(word in q_lower for word in ["story", "prophet", "قصة", "نبي"]):
            return QueryIntent.STORY_EXPLORATION

        if any(word in q_lower for word in ["theme", "topic", "about", "موضوع"]):
            return QueryIntent.THEME_SEARCH

        if any(word in q_lower for word in ["compare", "difference", "مقارنة", "فرق"]):
            return QueryIntent.COMPARATIVE

        if any(word in q_lower for word in ["root", "word", "grammar", "جذر", "كلمة"]):
            return QueryIntent.LINGUISTIC

        if any(word in q_lower for word in ["ruling", "halal", "haram", "allowed", "حكم", "حلال", "حرام"]):
            return QueryIntent.RULING

        # Default to verse meaning for Quran-related questions
        return QueryIntent.VERSE_MEANING

    def _build_context(
        self,
        chunks: List[RetrievedChunk],
        language: str,
    ) -> str:
        """
        Build context string from retrieved chunks.

        Groups by source and includes clear attribution.
        """
        context_parts = []

        # Group by reliability (primary vs secondary sources)
        primary = [c for c in chunks if c.relevance_score >= 0.7]
        secondary = [c for c in chunks if c.relevance_score < 0.7]

        if primary:
            context_parts.append("=== PRIMARY SOURCES ===\n")
            for chunk in primary:
                content = chunk.content_en if language == "en" else chunk.content_ar
                if not content:
                    content = chunk.content_ar or chunk.content_en or ""

                context_parts.append(f"""
[Source: {chunk.source_name} | Verse: {chunk.verse_reference} | ID: {chunk.chunk_id}]
{content[:2000]}  # Truncate long content
---
""")

        if secondary:
            context_parts.append("\n=== SECONDARY SOURCES ===\n")
            for chunk in secondary:
                content = chunk.content_en if language == "en" else chunk.content_ar
                if not content:
                    content = chunk.content_ar or chunk.content_en or ""

                context_parts.append(f"""
[Source: {chunk.source_name} | Verse: {chunk.verse_reference} | ID: {chunk.chunk_id}]
{content[:1500]}
---
""")

        return "".join(context_parts)

    async def _generate_response(
        self,
        question: str,
        context: str,
        intent: QueryIntent,
        language: str,
        include_scholarly_debate: bool,
    ) -> tuple[str, int]:
        """
        Generate response using the configured LLM provider.

        Returns:
            Tuple of (response_text, latency_ms)
        """
        if not self.llm:
            return SAFE_REFUSAL_NO_SOURCES, 0

        # Build user prompt
        user_prompt = build_user_prompt(
            question=question,
            context=context,
            language=language,
            include_scholarly_debate=include_scholarly_debate,
            is_fiqh=intent == QueryIntent.RULING,
        )

        try:
            response = await self.llm.generate(
                system_prompt=GROUNDED_SYSTEM_PROMPT,
                user_message=user_prompt,
                max_tokens=2000,
                temperature=0.3,  # Lower for factual/grounded responses
            )

            logger.info(
                f"LLM response: provider={self.llm_provider.value}, "
                f"tokens={response.tokens_used}, latency={response.latency_ms}ms"
            )

            return response.content, response.latency_ms

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}", 0

    async def _validate_and_parse_response(
        self,
        raw_response: str,
        chunks: List[RetrievedChunk],
        chunk_ids: List[str],
        intent: QueryIntent,
        query_expansion: Optional[ExpandedQuery] = None,
    ) -> GroundedResponse:
        """
        Validate citations and parse response into structured format
        with enhanced confidence scoring.
        """
        # Extract citations from response
        # Match both Latin (12:4) and Arabic-Indic numerals (١٢:٤)
        citation_pattern = r'\[([^\]]+)[,،]\s*([٠-٩\d]+:[٠-٩\d]+(?:-[٠-٩\d]+)?)\]'
        found_citations = re.findall(citation_pattern, raw_response)
        print(f"[CITATION] Found {len(found_citations)} citation patterns in response")
        print(f"[CITATION] Available chunks source_name: {[c.source_name for c in chunks[:3]]}...")
        print(f"[CITATION] Available chunks source_name_ar: {[getattr(c, 'source_name_ar', 'N/A') for c in chunks[:5]]}...")
        if found_citations:
            print(f"[CITATION] Sample citations: {found_citations[:3]}")

        # Map chunks by ID for quick lookup
        chunk_map = {c.chunk_id: c for c in chunks}

        # Build citation objects
        citations = []
        valid_citation_ids = set()
        invalid_count = 0

        def arabic_to_latin(s: str) -> str:
            """Convert Arabic-Indic numerals to Latin numerals."""
            arabic_nums = '٠١٢٣٤٥٦٧٨٩'
            latin_nums = '0123456789'
            for a, l in zip(arabic_nums, latin_nums):
                s = s.replace(a, l)
            return s

        def parse_verse_ref(ref: str) -> tuple:
            """Parse verse reference like '12:7' or '١٢:٧' into (sura, aya_start, aya_end)."""
            ref = arabic_to_latin(ref)
            if ':' not in ref:
                return (0, 0, 0)
            parts = ref.split(':')
            sura = int(parts[0])
            aya_part = parts[1]
            if '-' in aya_part:
                aya_parts = aya_part.split('-')
                return (sura, int(aya_parts[0]), int(aya_parts[1]))
            return (sura, int(aya_part), int(aya_part))

        def verse_overlaps(cited_ref: tuple, chunk_sura: int, chunk_aya_start: int, chunk_aya_end: int) -> bool:
            """Check if cited verse overlaps with chunk's verse range."""
            cited_sura, cited_aya_start, cited_aya_end = cited_ref
            if cited_sura != chunk_sura:
                return False
            # Check if ranges overlap
            return not (cited_aya_end < chunk_aya_start or cited_aya_start > chunk_aya_end)

        for source_name, verse_ref in found_citations:
            matched = False
            cited_verse = parse_verse_ref(verse_ref)

            # Find matching chunk (check both English and Arabic source names AND verse reference)
            for chunk in chunks:
                chunk_source_ar = getattr(chunk, 'source_name_ar', '') or ''
                # Check match in either English name, source_id, or Arabic name
                source_matches = (
                    source_name.lower() in chunk.source_name.lower() or
                    source_name.lower() in chunk.source_id.lower() or
                    source_name in chunk_source_ar
                )

                # Also check if the verse reference matches
                verse_matches = verse_overlaps(
                    cited_verse,
                    chunk.sura_no,
                    chunk.aya_start,
                    chunk.aya_end
                )

                # Match requires source AND verse to match (or verse is 0:0-0 for invalid parse)
                is_match = source_matches and (verse_matches or cited_verse == (0, 0, 0))

                if is_match:
                    if chunk.chunk_id not in valid_citation_ids:
                        print(f"[CITATION] Matched '{source_name}' verse {verse_ref} to chunk {chunk.chunk_id} ({chunk.verse_reference})")
                        citations.append(Citation(
                            chunk_id=chunk.chunk_id,
                            source_id=chunk.source_id,
                            source_name=chunk.source_name,
                            source_name_ar=getattr(chunk, 'source_name_ar', '') or chunk.source_name,
                            verse_reference=chunk.verse_reference,
                            excerpt=chunk.content[:200] if chunk.content else "",
                            relevance_score=chunk.relevance_score,
                        ))
                        valid_citation_ids.add(chunk.chunk_id)
                    # Count as matched even if chunk was already cited
                    matched = True
                    break

            if not matched:
                print(f"[CITATION] FAILED to match '{source_name}' verse {verse_ref}")
                invalid_count += 1

        # Count paragraphs and those with citations
        paragraphs = [p.strip() for p in raw_response.split('\n\n') if p.strip() and len(p.strip()) > 100]
        paragraphs_with_citations = sum(
            1 for p in paragraphs if re.search(citation_pattern, p)
        )

        # Get source reliability scores
        reliability_scores = [
            getattr(chunk, 'source_reliability', 0.8) for chunk in chunks
        ]
        relevance_scores = [chunk.relevance_score for chunk in chunks]

        # Check for primary sources
        has_primary = any(getattr(c, 'is_primary_source', True) for c in chunks)

        # Extract chunk and source IDs for evidence density calculation
        chunk_ids = [chunk.chunk_id for chunk in chunks if hasattr(chunk, 'chunk_id')]
        source_ids = [chunk.source_id for chunk in chunks if hasattr(chunk, 'source_id')]

        # Calculate enhanced confidence score
        print(f"[CONFIDENCE] valid_citations={len(citations)}, invalid={invalid_count}, paragraphs={len(paragraphs)}, with_citations={paragraphs_with_citations}")
        confidence_breakdown = confidence_scorer.calculate(
            total_paragraphs=len(paragraphs),
            paragraphs_with_citations=paragraphs_with_citations,
            valid_citations=len(citations),
            invalid_citations=invalid_count,
            source_reliability_scores=reliability_scores,
            relevance_scores=relevance_scores,
            has_primary_source=has_primary,
            unsupported_claims=0,  # TODO: Implement claim extraction
            chunk_ids=chunk_ids,
            source_ids=source_ids,
        )

        # Build warnings based on confidence
        warnings = []
        if confidence_breakdown.confidence_level == "insufficient":
            warnings.append("This response lacks sufficient scholarly source support.")
        elif confidence_breakdown.confidence_level == "low":
            warnings.append("This response has limited source support. Consider additional verification.")

        if invalid_count > 0:
            warnings.append(f"{invalid_count} citation(s) could not be validated against retrieved sources.")

        if not has_primary:
            warnings.append("No primary scholarly sources were used in this response.")

        # Add evidence density warning
        if not confidence_breakdown.evidence_density.is_sufficient:
            warnings.append(
                f"Limited evidence density: {confidence_breakdown.evidence_density.distinct_chunks} chunks, "
                f"{confidence_breakdown.evidence_density.distinct_sources} sources. "
                "Consider verifying with additional scholarly sources."
            )

        # Add fiqh warning if needed
        if intent == QueryIntent.RULING:
            warnings.append(SAFE_REFUSAL_FIQH)

        # Add confidence message
        confidence_message = get_confidence_message(confidence_breakdown.confidence_level)

        # Determine scholarly consensus if available
        consensus_votes = {}
        for chunk in chunks:
            if hasattr(chunk, 'scholarly_consensus') and chunk.scholarly_consensus:
                consensus_votes[chunk.scholarly_consensus] = (
                    consensus_votes.get(chunk.scholarly_consensus, 0) + 1
                )

        scholarly_consensus = None
        if consensus_votes:
            scholarly_consensus = max(consensus_votes, key=consensus_votes.get)

        return GroundedResponse(
            answer=raw_response,
            citations=citations,
            confidence=confidence_breakdown.final_score,
            confidence_level=confidence_breakdown.confidence_level,
            confidence_message=confidence_message,
            scholarly_consensus=scholarly_consensus,
            warnings=warnings,
            intent=intent.value,
            query_expansion=query_expansion.expansion_applied if query_expansion else None,
            degradation_reasons=confidence_breakdown.degradation_reasons,
            related_queries=[],  # TODO: Generate related queries
            # Evidence density (for user transparency)
            evidence_chunk_count=confidence_breakdown.evidence_density.distinct_chunks,
            evidence_source_count=confidence_breakdown.evidence_density.distinct_sources,
            # Raw evidence for transparency panel
            evidence=chunks,
            # API version for contract compatibility
            api_version=settings.api_version,
        )
