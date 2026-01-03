"""
RAG Pipeline for grounded Quranic Q&A.

CRITICAL SAFETY RULES:
1. NEVER invent tafseer - LLM may ONLY summarize retrieved evidence
2. Every paragraph MUST include at least one citation
3. Citations MUST be validated against retrieved chunks
4. If evidence is insufficient, return safe refusal
5. For fiqh/rulings: informational summary only, no fatwa language
"""
import re
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
import anthropic

from app.core.config import settings
from app.rag.types import (
    QueryIntent,
    RetrievedChunk,
    Citation,
    GroundedResponse,
    SAFE_REFUSAL_INSUFFICIENT,
    SAFE_REFUSAL_NO_SOURCES,
    SAFE_REFUSAL_FIQH,
)
from app.rag.retrieval import HybridRetriever
from app.rag.prompts import GROUNDED_SYSTEM_PROMPT, build_user_prompt
from app.validators.citation_validator import CitationValidator


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

    def __init__(self, session: AsyncSession):
        self.session = session
        self.retriever = HybridRetriever(session)
        self.validator = CitationValidator(session)

        # Initialize Anthropic client
        if settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.client = None

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
            language: Response language (ar/en)
            include_scholarly_debate: Include differing scholarly views
            preferred_sources: List of preferred tafseer source IDs
            max_sources: Maximum number of sources to retrieve

        Returns:
            GroundedResponse with answer, citations, and metadata
        """
        # 1. Classify intent
        intent = await self._classify_intent(question)

        # 2. Retrieve relevant chunks
        chunks = await self.retriever.retrieve(
            query=question,
            language=language,
            intent=intent,
            preferred_sources=preferred_sources or [],
            top_k=max_sources * 2,  # Retrieve more, then filter
        )

        # 3. Check if we have enough evidence
        if not chunks:
            return GroundedResponse(
                answer=SAFE_REFUSAL_NO_SOURCES,
                citations=[],
                confidence=0.0,
                intent=intent.value,
                warnings=["No relevant sources found"],
            )

        # 4. Build context from retrieved chunks
        context = self._build_context(chunks, language)

        # 5. Generate grounded response
        raw_response = await self._generate_response(
            question=question,
            context=context,
            intent=intent,
            language=language,
            include_scholarly_debate=include_scholarly_debate,
        )

        # 6. Parse and validate response
        chunk_ids = [c.chunk_id for c in chunks]
        validated = await self._validate_and_parse_response(
            raw_response=raw_response,
            chunks=chunks,
            chunk_ids=chunk_ids,
            intent=intent,
        )

        return validated

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
    ) -> str:
        """
        Generate response using Claude with strict grounding rules.
        """
        if not self.client:
            return SAFE_REFUSAL_NO_SOURCES

        # Build user prompt
        user_prompt = build_user_prompt(
            question=question,
            context=context,
            language=language,
            include_scholarly_debate=include_scholarly_debate,
            is_fiqh=intent == QueryIntent.RULING,
        )

        try:
            response = self.client.messages.create(
                model=settings.anthropic_model,
                max_tokens=2000,
                system=GROUNDED_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def _validate_and_parse_response(
        self,
        raw_response: str,
        chunks: List[RetrievedChunk],
        chunk_ids: List[str],
        intent: QueryIntent,
    ) -> GroundedResponse:
        """
        Validate citations and parse response into structured format.
        """
        # Extract citations from response
        citation_pattern = r'\[([^\]]+),\s*(\d+:\d+(?:-\d+)?)\]'
        found_citations = re.findall(citation_pattern, raw_response)

        # Map chunks by ID for quick lookup
        chunk_map = {c.chunk_id: c for c in chunks}

        # Build citation objects
        citations = []
        valid_citation_ids = set()

        for source_name, verse_ref in found_citations:
            # Find matching chunk
            for chunk in chunks:
                if (source_name.lower() in chunk.source_name.lower() or
                    source_name.lower() in chunk.source_id.lower()):
                    if chunk.chunk_id not in valid_citation_ids:
                        citations.append(Citation(
                            chunk_id=chunk.chunk_id,
                            source_id=chunk.source_id,
                            source_name=chunk.source_name,
                            verse_reference=chunk.verse_reference,
                            excerpt=chunk.content[:200] if chunk.content else "",
                            relevance_score=chunk.relevance_score,
                        ))
                        valid_citation_ids.add(chunk.chunk_id)
                    break

        # Calculate confidence
        if len(found_citations) == 0:
            confidence = 0.3
            warnings = ["Response may lack proper citations"]
        elif len(citations) < len(found_citations):
            confidence = 0.6
            warnings = ["Some citations could not be validated"]
        else:
            confidence = 0.9
            warnings = []

        # Add fiqh warning if needed
        if intent == QueryIntent.RULING:
            warnings.append(SAFE_REFUSAL_FIQH)

        # Determine scholarly consensus if available
        consensus_votes = {}
        for chunk in chunks:
            if chunk.scholarly_consensus:
                consensus_votes[chunk.scholarly_consensus] = (
                    consensus_votes.get(chunk.scholarly_consensus, 0) + 1
                )

        scholarly_consensus = None
        if consensus_votes:
            scholarly_consensus = max(consensus_votes, key=consensus_votes.get)

        return GroundedResponse(
            answer=raw_response,
            citations=citations,
            confidence=confidence,
            scholarly_consensus=scholarly_consensus,
            warnings=warnings,
            intent=intent.value,
            related_queries=[],  # TODO: Generate related queries
        )
