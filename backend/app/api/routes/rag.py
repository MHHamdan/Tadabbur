"""
RAG API routes for grounded Quranic Q&A.

CRITICAL: All responses MUST be grounded in retrieved sources.
NEVER generate tafseer without proper citations.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.core.config import settings
from app.rag.pipeline import RAGPipeline
from app.rag.types import QueryIntent

router = APIRouter()


# Request/Response schemas
class AskRequest(BaseModel):
    """Request schema for asking questions."""
    question: str = Field(..., min_length=5, max_length=1000)
    language: str = Field(default="en", pattern="^(ar|en)$")
    include_scholarly_debate: bool = Field(default=True)
    preferred_sources: List[str] = Field(default=[])
    max_sources: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate and clean question."""
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Question must be at least 5 characters")
        return v


class Citation(BaseModel):
    """Citation reference in response."""
    chunk_id: str
    source_id: str
    source_name: str
    verse_reference: str
    excerpt: str
    relevance_score: float


class GroundedResponse(BaseModel):
    """Grounded response with mandatory citations."""
    answer: str
    citations: List[Citation]
    confidence: float = Field(ge=0.0, le=1.0)
    scholarly_consensus: Optional[str] = None  # "agreed", "majority", "disputed"
    warnings: List[str] = []
    related_queries: List[str] = []
    intent: str
    processing_time_ms: int


class ValidationResult(BaseModel):
    """Citation validation result."""
    is_valid: bool
    valid_citations: List[str]
    invalid_citations: List[str]
    missing_citations: List[str]
    coverage_score: float


# Routes
@router.post("/ask", response_model=GroundedResponse)
async def ask_question(
    request: AskRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Ask a question about the Quran with grounded, cited response.

    SAFETY RULES:
    - All claims MUST be backed by retrieved tafseer chunks
    - Citations are MANDATORY and validated
    - If evidence is insufficient, returns safe refusal
    - For fiqh questions, clearly states this is informational only
    """
    start_time = datetime.now()

    # Check for API key
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="RAG service not configured. ANTHROPIC_API_KEY required."
        )

    try:
        # Initialize RAG pipeline
        pipeline = RAGPipeline(session)

        # Process query
        result = await pipeline.query(
            question=request.question,
            language=request.language,
            include_scholarly_debate=request.include_scholarly_debate,
            preferred_sources=request.preferred_sources,
            max_sources=request.max_sources,
        )

        # Calculate processing time
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        result.processing_time_ms = processing_time

        return result

    except Exception as e:
        # Log error and return safe response
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@router.post("/validate-citations", response_model=ValidationResult)
async def validate_citations(
    answer: str = Field(..., description="Answer text with citations"),
    retrieved_chunk_ids: List[str] = Field(..., description="List of retrieved chunk IDs"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Validate that all citations in an answer exist in retrieved sources.

    Used to verify RAG response integrity before displaying to users.
    """
    from app.validators.citation_validator import CitationValidator

    validator = CitationValidator(session)
    result = await validator.validate(answer, retrieved_chunk_ids)

    return ValidationResult(
        is_valid=result.is_valid,
        valid_citations=result.valid_citations,
        invalid_citations=result.invalid_citations,
        missing_citations=result.missing_citations,
        coverage_score=result.coverage_score,
    )


@router.get("/intents")
async def get_query_intents():
    """
    Get available query intent types.
    """
    return {
        "intents": [
            {
                "id": "verse_meaning",
                "name_en": "Verse Meaning",
                "name_ar": "معنى الآية",
                "description": "Questions about the meaning of specific verses",
            },
            {
                "id": "story_exploration",
                "name_en": "Story Exploration",
                "name_ar": "استكشاف القصة",
                "description": "Questions about prophets and Quranic stories",
            },
            {
                "id": "theme_search",
                "name_en": "Theme Search",
                "name_ar": "البحث عن موضوع",
                "description": "Questions about topics and themes in Quran",
            },
            {
                "id": "comparative",
                "name_en": "Comparative",
                "name_ar": "مقارنة",
                "description": "Comparing verses or interpretations",
            },
            {
                "id": "linguistic",
                "name_en": "Linguistic",
                "name_ar": "لغوي",
                "description": "Arabic grammar, root words, rhetoric",
            },
            {
                "id": "ruling",
                "name_en": "Ruling (Informational)",
                "name_ar": "الحكم (معلوماتي)",
                "description": "Fiqh-related questions (informational only, not fatwa)",
            },
        ]
    }


@router.get("/sample-questions")
async def get_sample_questions(
    language: str = Query("en", pattern="^(ar|en)$"),
):
    """
    Get sample questions for each intent type.
    """
    samples = {
        "en": [
            {
                "intent": "verse_meaning",
                "question": "What is the meaning of Ayat al-Kursi (2:255)?",
            },
            {
                "intent": "story_exploration",
                "question": "Tell me about the story of Prophet Yusuf and his brothers",
            },
            {
                "intent": "theme_search",
                "question": "What does the Quran say about patience (sabr)?",
            },
            {
                "intent": "comparative",
                "question": "How is the story of Musa narrated differently in Surah Al-Qasas vs Surah Taha?",
            },
            {
                "intent": "linguistic",
                "question": "What is the root word and meaning of 'taqwa'?",
            },
        ],
        "ar": [
            {
                "intent": "verse_meaning",
                "question": "ما معنى آية الكرسي؟",
            },
            {
                "intent": "story_exploration",
                "question": "أخبرني عن قصة يوسف عليه السلام مع إخوته",
            },
            {
                "intent": "theme_search",
                "question": "ماذا يقول القرآن عن الصبر؟",
            },
        ],
    }

    return {"language": language, "samples": samples.get(language, samples["en"])}


@router.get("/sources")
async def get_available_sources(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get available tafseer sources for RAG.
    """
    from sqlalchemy import select
    from app.models.tafseer import TafseerSource

    result = await session.execute(
        select(TafseerSource).order_by(TafseerSource.reliability_score.desc())
    )
    sources = result.scalars().all()

    return {
        "sources": [
            {
                "id": s.id,
                "name_ar": s.name_ar,
                "name_en": s.name_en,
                "author": s.author_en,
                "methodology": s.methodology,
                "language": s.language,
                "reliability_score": s.reliability_score,
            }
            for s in sources
        ]
    }
