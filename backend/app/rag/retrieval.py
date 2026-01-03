"""
Hybrid retrieval combining vector search and keyword search.
"""
from typing import List, Optional

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.core.config import settings
from app.models.tafseer import TafseerChunk, TafseerSource
from app.rag.types import QueryIntent, RetrievedChunk


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
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.qdrant = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )

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
        """
        # 1. Expand query with Islamic terminology
        expanded_terms = self._expand_query(query)
        expanded_query = query + " " + " ".join(expanded_terms)

        # 2. Vector search
        vector_results = await self._vector_search(
            query=expanded_query,
            language=language,
            preferred_sources=preferred_sources,
            top_k=top_k,
        )

        # 3. Keyword search
        keyword_results = await self._keyword_search(
            query=query,
            expanded_terms=expanded_terms,
            language=language,
            preferred_sources=preferred_sources,
            top_k=top_k,
        )

        # 4. Merge results with RRF
        merged = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            k=60,  # RRF constant
        )

        # 5. Limit to top_k
        return merged[:top_k]

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

    async def _vector_search(
        self,
        query: str,
        language: str,
        preferred_sources: List[str],
        top_k: int,
    ) -> List[RetrievedChunk]:
        """
        Search using vector embeddings in Qdrant.
        """
        try:
            # Build filter
            filter_conditions = []
            if preferred_sources:
                filter_conditions.append(
                    FieldCondition(
                        key="source_id",
                        match=MatchValue(any=preferred_sources),
                    )
                )

            search_filter = Filter(must=filter_conditions) if filter_conditions else None

            # For MVP, we use a simple search
            # In production, we'd use proper embeddings
            results = self.qdrant.search(
                collection_name=settings.qdrant_collection_tafseer,
                query_vector=[0.0] * settings.embedding_dimension,  # Placeholder
                query_filter=search_filter,
                limit=top_k,
                with_payload=True,
            )

            chunks = []
            for result in results:
                payload = result.payload or {}
                chunks.append(
                    RetrievedChunk(
                        chunk_id=payload.get("chunk_id", ""),
                        source_id=payload.get("source_id", ""),
                        source_name=payload.get("source_name", ""),
                        source_name_ar=payload.get("source_name_ar", ""),
                        verse_reference=payload.get("verse_reference", ""),
                        sura_no=payload.get("sura_no", 0),
                        aya_start=payload.get("aya_start", 0),
                        aya_end=payload.get("aya_end", 0),
                        content=payload.get(f"content_{language}", ""),
                        content_ar=payload.get("content_ar"),
                        content_en=payload.get("content_en"),
                        relevance_score=result.score,
                        scholarly_consensus=payload.get("scholarly_consensus"),
                    )
                )

            return chunks

        except Exception as e:
            # Vector DB might not be ready, fall back to keyword only
            print(f"Vector search error: {e}")
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
        """
        # Build search terms
        all_terms = [query] + expanded_terms
        search_pattern = "%{}%".format(query.replace(" ", "%"))

        # Build query
        content_column = TafseerChunk.content_en if language == "en" else TafseerChunk.content_ar

        stmt = (
            select(TafseerChunk, TafseerSource)
            .join(TafseerSource, TafseerChunk.source_id == TafseerSource.id)
            .where(
                or_(
                    content_column.ilike(search_pattern),
                    TafseerChunk.topics.overlap(all_terms) if expanded_terms else False,
                )
            )
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

        # Score vector results
        for rank, chunk in enumerate(vector_results, start=1):
            chunk_id = chunk.chunk_id
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1 / (k + rank)
            chunk_map[chunk_id] = chunk

        # Score keyword results
        for rank, chunk in enumerate(keyword_results, start=1):
            chunk_id = chunk.chunk_id
            chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0) + 1 / (k + rank)
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk

        # Sort by RRF score
        sorted_ids = sorted(chunk_scores.keys(), key=lambda x: chunk_scores[x], reverse=True)

        # Update relevance scores and return
        result = []
        for chunk_id in sorted_ids:
            chunk = chunk_map[chunk_id]
            chunk.relevance_score = min(chunk_scores[chunk_id] * 5, 1.0)  # Normalize
            result.append(chunk)

        return result
