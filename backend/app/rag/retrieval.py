"""
Hybrid retrieval combining vector search and keyword search.

LANGUAGE POLICY:
================
This retrieval module ONLY supports Arabic (ar) and English (en) for RAG operations.

- Vector search embeddings are computed for Arabic and English content only
- Keyword search (FTS) operates on Arabic and English tafseer text
- Any other language parameter will be coerced to "en" with a warning

Other languages (Urdu, Indonesian, etc.) are DISPLAY-ONLY and served from
the translations table via separate endpoints, NOT through RAG retrieval.
"""
import logging
from typing import List, Optional

import httpx
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.tafseer import TafseerChunk, TafseerSource
from app.rag.types import QueryIntent, RetrievedChunk, RAG_SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


# Islamic terminology expansion glossary
TERM_GLOSSARY = {
    # English to Arabic equivalents
    "patience": ["sabr", "صبر"],
    "trust": ["tawakkul", "توكل"],
    "faith": ["iman", "إيمان"],
    "prayer": ["salah", "salat", "صلاة"],
    "fasting": ["sawm", "siyam", "صوم", "صيام"],
    "charity": ["zakat", "sadaqah", "زكاة", "صدقة"],
    "pilgrimage": ["hajj", "حج"],
    "god": ["allah", "الله"],
    "messenger": ["rasul", "رسول"],
    "prophet": ["nabi", "نبي"],
    "angels": ["malaika", "ملائكة"],
    "heaven": ["jannah", "جنة"],
    "hell": ["jahannam", "نار", "جهنم"],
    "quran": ["qur'an", "القرآن"],
    "verse": ["ayah", "آية"],
    "chapter": ["surah", "سورة"],
    # Arabic to English
    "صبر": ["patience", "sabr"],
    "توكل": ["trust", "reliance", "tawakkul"],
    "إيمان": ["faith", "belief", "iman"],
}


class HybridRetriever:
    """
    Hybrid retrieval combining:
    1. Vector search in Qdrant
    2. Keyword search in PostgreSQL (FTS)
    3. Reciprocal Rank Fusion for merging results

    SAFETY: Only retrieves from ENABLED sources (is_enabled=True).
    """

    # Safety limits for evidence content
    MAX_CHUNK_CONTENT_LENGTH = 2000  # Max chars per chunk for display
    MAX_CHUNKS_IN_RESPONSE = 8  # Max evidence chunks to return

    def __init__(self, session: AsyncSession):
        self.session = session
        # Use HTTP API directly to avoid qdrant-client version issues
        self.qdrant_url = f"http://{settings.qdrant_host}:{settings.qdrant_port}"
        self.embedding_model = None  # Lazy-loaded
        self._enabled_sources_cache: set = None  # Cache enabled source IDs

    async def _get_enabled_source_ids(self) -> set:
        """
        Get set of enabled source IDs from the database.
        Cached per retriever instance to avoid repeated queries.
        """
        if self._enabled_sources_cache is not None:
            return self._enabled_sources_cache

        result = await self.session.execute(
            select(TafseerSource.id).where(TafseerSource.is_enabled == 1)
        )
        self._enabled_sources_cache = {row[0] for row in result.fetchall()}
        logger.info(f"Cached {len(self._enabled_sources_cache)} enabled sources")
        return self._enabled_sources_cache

    def _truncate_content(self, content: str, max_length: int = None) -> str:
        """Truncate content to max length with ellipsis if needed."""
        if max_length is None:
            max_length = self.MAX_CHUNK_CONTENT_LENGTH
        if content and len(content) > max_length:
            return content[:max_length - 3] + "..."
        return content or ""

    async def retrieve(
        self,
        query: str,
        language: str = "en",
        intent: QueryIntent = QueryIntent.VERSE_MEANING,
        preferred_sources: List[str] = None,
        top_k: int = 10,
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks using hybrid search.

        Args:
            query: The search query
            language: Response language (ar/en ONLY - see LANGUAGE POLICY)
            intent: Query intent for filtering
            preferred_sources: List of preferred tafseer source IDs
            top_k: Maximum number of chunks to return

        Returns:
            List of RetrievedChunk objects with tafseer content

        Note:
            Language MUST be 'ar' or 'en'. Other languages are display-only
            and served from the translations table, not RAG retrieval.
        """
        # Validate and coerce language to RAG-supported language
        if language not in RAG_SUPPORTED_LANGUAGES:
            logger.warning(
                f"Language '{language}' not supported for RAG retrieval. "
                f"Coercing to 'en'. Supported: {RAG_SUPPORTED_LANGUAGES}"
            )
            language = "en"

        # 1. Expand query with Islamic terminology
        expanded_terms = self._expand_query(query)
        expanded_query = query + " " + " ".join(expanded_terms)
        print(f"[RETRIEVAL] Query: {query[:50]}..., Expanded terms: {expanded_terms}")

        # 2. Vector search
        vector_results = await self._vector_search(
            query=expanded_query,
            language=language,
            preferred_sources=preferred_sources,
            top_k=top_k,
        )
        print(f"[RETRIEVAL] Vector search returned: {len(vector_results)} results")

        # 3. Keyword search
        keyword_results = await self._keyword_search(
            query=query,
            expanded_terms=expanded_terms,
            language=language,
            preferred_sources=preferred_sources,
            top_k=top_k,
        )
        print(f"[RETRIEVAL] Keyword search returned: {len(keyword_results)} results")

        # 4. Merge results with RRF
        merged = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            k=60,  # RRF constant
        )
        print(f"[RETRIEVAL] Merged results: {len(merged)}, returning top {top_k}")

        # 5. Limit to top_k AND MAX_CHUNKS_IN_RESPONSE (safety limit)
        max_results = min(top_k, self.MAX_CHUNKS_IN_RESPONSE)
        final_results = merged[:max_results]

        # 6. Truncate content for safety (prevent huge payloads)
        for chunk in final_results:
            chunk.content = self._truncate_content(chunk.content)
            if chunk.content_ar:
                chunk.content_ar = self._truncate_content(chunk.content_ar)
            if chunk.content_en:
                chunk.content_en = self._truncate_content(chunk.content_en)

        return final_results

    def _expand_query(self, query: str) -> List[str]:
        """
        Expand query with Islamic terminology equivalents.
        """
        expanded = []
        query_lower = query.lower()

        for term, equivalents in TERM_GLOSSARY.items():
            if term.lower() in query_lower:
                expanded.extend(equivalents)

        return list(set(expanded))

    def _get_embedding_model(self):
        """Lazy-load the embedding model."""
        if self.embedding_model is None:
            import os
            import torch
            from sentence_transformers import SentenceTransformer

            # Use GPU if available, otherwise CPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            # Allow override via environment variable
            device = os.environ.get("EMBEDDING_DEVICE", device)

            logger.info(f"Loading embedding model on device: {device}")
            self.embedding_model = SentenceTransformer(
                settings.embedding_model_multilingual,
                device=device,
            )
        return self.embedding_model

    async def _vector_search(
        self,
        query: str,
        language: str,
        preferred_sources: List[str],
        top_k: int,
    ) -> List[RetrievedChunk]:
        """
        Search using vector embeddings in Qdrant via HTTP API.

        SAFETY: Filters results to only include ENABLED sources.
        """
        try:
            # Get enabled sources for filtering
            enabled_sources = await self._get_enabled_source_ids()
            if not enabled_sources:
                logger.warning("No enabled sources found - returning empty results")
                return []

            # Generate query embedding
            model = self._get_embedding_model()
            # E5 models need "query: " prefix for queries
            query_text = f"query: {query}"
            query_vector = model.encode(query_text).tolist()

            # Build search request - fetch extra to account for filtering
            search_body = {
                "vector": query_vector,
                "limit": top_k * 2,  # Fetch extra to account for disabled source filtering
                "with_payload": True,
            }

            # Add filter if preferred sources specified (intersect with enabled)
            if preferred_sources:
                # Only include preferred sources that are also enabled
                valid_sources = [s for s in preferred_sources if s in enabled_sources]
                if not valid_sources:
                    logger.warning("None of the preferred sources are enabled")
                    return []
                search_body["filter"] = {
                    "must": [
                        {
                            "key": "source_id",
                            "match": {"any": valid_sources},
                        }
                    ]
                }

            # Execute search via HTTP
            logger.info(f"Vector search: querying Qdrant with {len(query_vector)} dim vector")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.qdrant_url}/collections/{settings.qdrant_collection_tafseer}/points/search",
                    json=search_body,
                )
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "ok":
                logger.warning(f"Qdrant search failed: {data}")
                return []

            logger.info(f"Vector search returned {len(data.get('result', []))} results")

            # Parse results and filter by enabled sources
            chunks = []
            filtered_count = 0
            for result in data.get("result", []):
                payload = result.get("payload", {})
                source_id = payload.get("source_id", "")

                # SAFETY: Skip results from disabled sources
                if source_id not in enabled_sources:
                    filtered_count += 1
                    continue

                score = result.get("score", 0.0)
                if len(chunks) < 3:  # Log first 3 scores
                    print(f"[VECTOR] Raw Qdrant score: {score}")

                chunks.append(
                    RetrievedChunk(
                        chunk_id=payload.get("chunk_id", ""),
                        source_id=source_id,
                        source_name=payload.get("source_name", ""),
                        source_name_ar=payload.get("source_name_ar", ""),
                        verse_reference=payload.get("verse_reference", ""),
                        sura_no=payload.get("sura_no", 0),
                        aya_start=payload.get("aya_start", 0),
                        aya_end=payload.get("aya_end", 0),
                        content=payload.get(f"content_{language}", ""),
                        content_ar=payload.get("content_ar"),
                        content_en=payload.get("content_en"),
                        relevance_score=result.get("score", 0.0),
                        scholarly_consensus=payload.get("scholarly_consensus"),
                    )
                )

                # Stop once we have enough results
                if len(chunks) >= top_k:
                    break

            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} results from disabled sources")

            return chunks

        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    async def _keyword_search(
        self,
        query: str,
        expanded_terms: List[str],
        language: str,
        preferred_sources: List[str],
        top_k: int,
    ) -> List[RetrievedChunk]:
        """
        Search using PostgreSQL keyword matching.

        SAFETY: Only searches ENABLED sources.
        """
        # Extract meaningful keywords from query (filter out common words)
        stop_words = {
            'عن', 'في', 'من', 'إلى', 'على', 'ما', 'هل', 'كيف', 'ماذا', 'لماذا',
            'أخبرني', 'حدثني', 'اشرح', 'وضح', 'قصة', 'قصص',
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why',
            'tell', 'me', 'about', 'explain', 'story', 'of'
        }

        # Split query into words and filter
        words = query.replace('؟', '').replace('?', '').split()
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 2]

        # Add expanded terms
        all_keywords = keywords + expanded_terms

        if not all_keywords:
            logger.warning(f"No keywords extracted from query: {query}")
            return []

        logger.info(f"Keyword search with terms: {all_keywords}")

        # Build query - search for each keyword with OR
        content_column = TafseerChunk.content_en if language == "en" else TafseerChunk.content_ar

        # Build OR conditions for each keyword
        conditions = []
        for keyword in all_keywords:
            conditions.append(content_column.ilike(f"%{keyword}%"))

        stmt = (
            select(TafseerChunk, TafseerSource)
            .join(TafseerSource, TafseerChunk.source_id == TafseerSource.id)
            .where(or_(*conditions))
            # SAFETY: Only include enabled sources (is_enabled is INTEGER: 1=enabled, 0=disabled)
            .where(TafseerSource.is_enabled == 1)
        )

        if preferred_sources:
            stmt = stmt.where(TafseerChunk.source_id.in_(preferred_sources))

        stmt = stmt.limit(top_k)

        result = await self.session.execute(stmt)
        rows = result.all()

        chunks = []
        for chunk, source in rows:
            content = chunk.content_en if language == "en" else chunk.content_ar
            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    source_name=source.name_en,
                    source_name_ar=source.name_ar,
                    verse_reference=chunk.verse_reference,
                    sura_no=chunk.sura_no,
                    aya_start=chunk.aya_start,
                    aya_end=chunk.aya_end,
                    content=content or "",
                    content_ar=chunk.content_ar,
                    content_en=chunk.content_en,
                    relevance_score=0.5,  # Base score for keyword matches
                    scholarly_consensus=chunk.scholarly_consensus,
                )
            )

        return chunks

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[RetrievedChunk],
        keyword_results: List[RetrievedChunk],
        k: int = 60,
    ) -> List[RetrievedChunk]:
        """
        Merge results using Reciprocal Rank Fusion.

        RRF score = sum(1 / (k + rank)) for each list where document appears
        """
        chunk_scores = {}
        chunk_map = {}
        original_scores = {}  # Keep track of original vector search scores

        # Score vector results
        for rank, chunk in enumerate(vector_results, start=1):
            chunk_id = chunk.chunk_id
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1 / (k + rank)
            chunk_map[chunk_id] = chunk
            # Keep original vector score if higher
            if chunk_id not in original_scores:
                original_scores[chunk_id] = chunk.relevance_score
            else:
                original_scores[chunk_id] = max(original_scores[chunk_id], chunk.relevance_score)

        # Score keyword results
        for rank, chunk in enumerate(keyword_results, start=1):
            chunk_id = chunk.chunk_id
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1 / (k + rank)
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk
            # Keep original keyword score if higher
            if chunk_id not in original_scores:
                original_scores[chunk_id] = chunk.relevance_score
            else:
                original_scores[chunk_id] = max(original_scores[chunk_id], chunk.relevance_score)

        # Sort by RRF score
        sorted_ids = sorted(chunk_scores.keys(), key=lambda x: chunk_scores[x], reverse=True)

        # Calculate max RRF score for normalization
        # Max possible = 1/(k+1) + 1/(k+1) = 2/(k+1) if doc appears at rank 1 in both lists
        max_rrf = 2 / (k + 1)

        # Update relevance scores and return
        result = []
        for chunk_id in sorted_ids:
            chunk = chunk_map[chunk_id]
            # Normalize RRF score to 0-1 range, then blend with original score
            rrf_normalized = min(chunk_scores[chunk_id] / max_rrf, 1.0)
            original_score = original_scores.get(chunk_id, 0.5)
            # Use max of normalized RRF and original score, but boost if in both lists
            in_both_lists = chunk_scores[chunk_id] > 1 / (k + 1)  # More than single list contribution
            if in_both_lists:
                # Boost score for appearing in both lists
                chunk.relevance_score = min((rrf_normalized + original_score) / 2 + 0.3, 1.0)
            else:
                # Use max of the two
                chunk.relevance_score = max(rrf_normalized, original_score)
            result.append(chunk)

        return result
