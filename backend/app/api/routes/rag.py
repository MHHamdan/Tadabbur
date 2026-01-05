"""
RAG API routes for grounded Quranic Q&A.

CRITICAL: All responses MUST be grounded in retrieved sources.
NEVER generate tafseer without proper citations.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Header
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
    source_name_ar: str
    verse_reference: str
    excerpt: str
    relevance_score: float


class EvidenceChunk(BaseModel):
    """Raw evidence chunk for transparency panel."""
    chunk_id: str
    source_id: str
    source_name: str
    source_name_ar: str
    verse_reference: str
    sura_no: int
    aya_start: int
    aya_end: int
    content: str
    content_ar: Optional[str] = None
    content_en: Optional[str] = None
    relevance_score: float
    methodology: Optional[str] = None


class EvidenceDensity(BaseModel):
    """Evidence density metadata for transparency."""
    chunk_count: int = Field(ge=0, description="Number of distinct evidence chunks used")
    source_count: int = Field(ge=0, description="Number of distinct tafseer sources used")


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
    # Evidence density for user transparency (read-only, no raw IDs)
    evidence_density: Optional[EvidenceDensity] = None
    # Raw evidence chunks for transparency panel
    evidence: List[EvidenceChunk] = []


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

    # Check for LLM provider configuration
    if settings.llm_provider == "claude" and not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="RAG service not configured. ANTHROPIC_API_KEY required for Claude provider."
        )
    elif settings.llm_provider == "ollama":
        # Verify Ollama is accessible
        import httpx
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=503,
                        detail="Ollama service not available. Ensure Ollama is running."
                    )
        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Ollama. Ensure Ollama is running on the configured URL."
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

        # Convert to dict for proper serialization
        return result.to_dict()

    except Exception as e:
        # Log error and return safe response
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


class ValidateCitationsRequest(BaseModel):
    """Request schema for citation validation."""
    answer: str = Field(..., description="Answer text with citations")
    retrieved_chunk_ids: List[str] = Field(..., description="List of retrieved chunk IDs")


@router.post("/validate-citations", response_model=ValidationResult)
async def validate_citations(
    request: ValidateCitationsRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Validate that all citations in an answer exist in retrieved sources.

    Used to verify RAG response integrity before displaying to users.
    """
    from app.validators.citation_validator import CitationValidator

    validator = CitationValidator(session)
    result = await validator.validate(request.answer, request.retrieved_chunk_ids)

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


class TafseerSourceInfo(BaseModel):
    """Tafseer source information with provenance."""
    id: str
    name_ar: str
    name_en: str
    author_ar: Optional[str] = None
    author_en: Optional[str] = None
    methodology: Optional[str] = None
    era: Optional[str] = None
    language: str
    reliability_score: float
    is_primary_source: bool
    is_enabled: bool = True  # Admin control

    # Provenance (for transparency)
    version_tag: Optional[str] = None
    license_type: Optional[str] = None
    license: Optional[str] = None
    license_verified: bool = False
    has_valid_provenance: bool = False
    ayah_count: Optional[int] = None


class SourcesResponse(BaseModel):
    """Response containing all tafseer sources."""
    sources: List[TafseerSourceInfo]
    count: int
    provenance_verified: int  # Number with valid provenance


@router.get("/sources", response_model=SourcesResponse)
async def get_available_sources(
    language: str = Query(None, pattern="^(ar|en)$", description="Filter by language"),
    include_provenance: bool = Query(True, description="Include provenance metadata"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get available tafseer sources with full transparency.

    This endpoint exposes:
    - Source metadata (name, author, methodology)
    - Provenance data (version, license, verification status)
    - Quality indicators (reliability score, primary source status)

    NOTE: This PUBLIC endpoint only returns ENABLED sources.
    Use /admin/sources with admin token to see all sources.

    Used for:
    - Mobile app source selection
    - Transparency about data origins
    - Citation verification
    """
    from sqlalchemy import select
    from app.models.tafseer import TafseerSource

    # PUBLIC endpoint: Only return ENABLED sources (is_enabled is INTEGER: 1=enabled, 0=disabled)
    query = (
        select(TafseerSource)
        .where(TafseerSource.is_enabled == 1)
        .order_by(TafseerSource.reliability_score.desc())
    )

    if language:
        query = query.where(TafseerSource.language == language)

    result = await session.execute(query)
    sources = result.scalars().all()

    source_infos = []
    provenance_verified = 0

    for s in sources:
        has_provenance = s.has_valid_provenance
        if has_provenance:
            provenance_verified += 1

        info = TafseerSourceInfo(
            id=s.id,
            name_ar=s.name_ar,
            name_en=s.name_en,
            author_ar=s.author_ar,
            author_en=s.author_en,
            methodology=s.methodology,
            era=s.era,
            language=s.language,
            reliability_score=s.reliability_score or 0.0,
            is_primary_source=bool(s.is_primary_source),
            is_enabled=bool(s.is_enabled) if s.is_enabled is not None else True,
            version_tag=s.version_tag if include_provenance else None,
            license_type=s.license_type if include_provenance else None,
            license=s.license if include_provenance else None,
            license_verified=bool(s.license_verified) if include_provenance else False,
            has_valid_provenance=has_provenance,
            ayah_count=s.ayah_count if include_provenance else None,
        )
        source_infos.append(info)

    return SourcesResponse(
        sources=source_infos,
        count=len(source_infos),
        provenance_verified=provenance_verified,
    )


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

class ToggleSourceRequest(BaseModel):
    """Request to toggle source enabled status."""
    is_enabled: bool


class ToggleSourceResponse(BaseModel):
    """Response from toggling source."""
    source_id: str
    is_enabled: bool
    message: str


def verify_admin_token(x_admin_token: str = Header(..., description="Admin token for authentication")):
    """
    Verify admin token from X-Admin-Token header.

    SECURITY: Admin token MUST be sent via header, never via query parameter.
    Query parameters leak in browser history, server logs, and Referer headers.
    """
    if not settings.admin_token:
        raise HTTPException(
            status_code=503,
            detail="Admin token not configured. Set ADMIN_TOKEN environment variable."
        )
    if x_admin_token != settings.admin_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token"
        )
    return True


@router.put("/admin/sources/{source_id}/toggle", response_model=ToggleSourceResponse)
async def toggle_source_enabled(
    source_id: str,
    request: ToggleSourceRequest,
    session: AsyncSession = Depends(get_async_session),
    _: bool = Depends(verify_admin_token),
):
    """
    Enable or disable a tafseer source for RAG.

    Requires admin token authentication.
    Disabled sources will not be retrieved for RAG queries.
    """
    from sqlalchemy import select, update
    from app.models.tafseer import TafseerSource

    # Check if source exists
    result = await session.execute(
        select(TafseerSource).where(TafseerSource.id == source_id)
    )
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(
            status_code=404,
            detail=f"Source '{source_id}' not found"
        )

    # Update source
    await session.execute(
        update(TafseerSource)
        .where(TafseerSource.id == source_id)
        .values(is_enabled=1 if request.is_enabled else 0)
    )
    await session.commit()

    status = "enabled" if request.is_enabled else "disabled"
    return ToggleSourceResponse(
        source_id=source_id,
        is_enabled=request.is_enabled,
        message=f"Source '{source_id}' has been {status}"
    )


@router.get("/admin/sources", response_model=SourcesResponse)
async def get_all_sources_admin(
    session: AsyncSession = Depends(get_async_session),
    _: bool = Depends(verify_admin_token),
):
    """
    Get all sources including disabled ones (admin only).
    """
    from sqlalchemy import select
    from app.models.tafseer import TafseerSource

    query = select(TafseerSource).order_by(TafseerSource.reliability_score.desc())
    result = await session.execute(query)
    sources = result.scalars().all()

    source_infos = []
    provenance_verified = 0

    for s in sources:
        has_provenance = s.has_valid_provenance
        if has_provenance:
            provenance_verified += 1

        info = TafseerSourceInfo(
            id=s.id,
            name_ar=s.name_ar,
            name_en=s.name_en,
            author_ar=s.author_ar,
            author_en=s.author_en,
            methodology=s.methodology,
            era=s.era,
            language=s.language,
            reliability_score=s.reliability_score or 0.0,
            is_primary_source=bool(s.is_primary_source),
            is_enabled=bool(s.is_enabled) if s.is_enabled is not None else True,
            version_tag=s.version_tag,
            license_type=s.license_type,
            license=s.license,
            license_verified=bool(s.license_verified),
            has_valid_provenance=has_provenance,
            ayah_count=s.ayah_count,
        )
        source_infos.append(info)

    return SourcesResponse(
        sources=source_infos,
        count=len(source_infos),
        provenance_verified=provenance_verified,
    )
