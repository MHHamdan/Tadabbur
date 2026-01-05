"""
Quran API routes for verses, translations, and tafseer.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_async_session
from app.models.quran import QuranVerse, Translation
from app.models.tafseer import TafseerChunk, TafseerSource

router = APIRouter()


# Pydantic schemas
class TranslationResponse(BaseModel):
    """Translation response schema."""
    language: str
    translator: str
    text: str

    class Config:
        from_attributes = True


class VerseResponse(BaseModel):
    """Verse response schema."""
    id: int
    sura_no: int
    sura_name_ar: str
    sura_name_en: str
    aya_no: int
    text_uthmani: str
    text_imlaei: str
    page_no: int
    juz_no: int
    translations: List[TranslationResponse] = []

    class Config:
        from_attributes = True


class TafseerChunkResponse(BaseModel):
    """Tafseer chunk response schema."""
    chunk_id: str
    source_id: str
    source_name: Optional[str] = None
    verse_reference: str
    content_ar: Optional[str] = None
    content_en: Optional[str] = None
    scholarly_consensus: Optional[str] = None

    class Config:
        from_attributes = True


class SuraMetadata(BaseModel):
    """Sura metadata response."""
    sura_no: int
    name_ar: str
    name_en: str
    total_verses: int
    revelation_type: Optional[str] = None


# Routes
@router.get("/metadata")
async def get_quran_metadata(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get Quran metadata - total verses, suras, etc.
    """
    result = await session.execute(
        select(QuranVerse.sura_no, QuranVerse.sura_name_ar, QuranVerse.sura_name_en)
        .distinct()
        .order_by(QuranVerse.sura_no)
    )
    suras = result.all()

    # Get verse count per sura
    verse_counts = await session.execute(
        select(QuranVerse.sura_no, QuranVerse.id)
    )
    verse_count_map = {}
    for row in verse_counts.all():
        sura_no = row[0]
        verse_count_map[sura_no] = verse_count_map.get(sura_no, 0) + 1

    return {
        "total_verses": sum(verse_count_map.values()),
        "total_suras": len(suras),
        "suras": [
            {
                "sura_no": s[0],
                "name_ar": s[1],
                "name_en": s[2],
                "total_verses": verse_count_map.get(s[0], 0),
            }
            for s in suras
        ],
    }


@router.get("/suras/{sura_no}", response_model=List[VerseResponse])
async def get_sura_verses(
    sura_no: int,
    include_translations: bool = Query(True, description="Include translations"),
    language: Optional[str] = Query(None, description="Filter translations by language"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get all verses for a specific sura.
    """
    if sura_no < 1 or sura_no > 114:
        raise HTTPException(status_code=400, detail="Sura number must be between 1 and 114")

    query = select(QuranVerse).where(QuranVerse.sura_no == sura_no).order_by(QuranVerse.aya_no)

    if include_translations:
        query = query.options(selectinload(QuranVerse.translations))

    result = await session.execute(query)
    verses = result.scalars().all()

    if not verses:
        raise HTTPException(status_code=404, detail=f"Sura {sura_no} not found")

    # Filter translations by language if specified
    response = []
    for verse in verses:
        verse_data = VerseResponse.model_validate(verse)
        if language and verse.translations:
            verse_data.translations = [
                TranslationResponse.model_validate(t)
                for t in verse.translations
                if t.language == language
            ]
        response.append(verse_data)

    return response


@router.get("/verses/{sura_no}/{aya_no}", response_model=VerseResponse)
async def get_verse(
    sura_no: int,
    aya_no: int,
    include_translations: bool = Query(True),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific verse by sura and aya number.
    """
    query = select(QuranVerse).where(
        QuranVerse.sura_no == sura_no,
        QuranVerse.aya_no == aya_no,
    )

    if include_translations:
        query = query.options(selectinload(QuranVerse.translations))

    result = await session.execute(query)
    verse = result.scalar_one_or_none()

    if not verse:
        raise HTTPException(
            status_code=404, detail=f"Verse {sura_no}:{aya_no} not found"
        )

    return VerseResponse.model_validate(verse)


@router.get("/verses/{sura_no}/{aya_start}/{aya_end}", response_model=List[VerseResponse])
async def get_verse_range(
    sura_no: int,
    aya_start: int,
    aya_end: int,
    include_translations: bool = Query(True),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get a range of verses from a sura.
    """
    if sura_no < 1 or sura_no > 114:
        raise HTTPException(status_code=400, detail="Sura number must be between 1 and 114")
    if aya_start > aya_end:
        raise HTTPException(status_code=400, detail="aya_start must be <= aya_end")

    query = select(QuranVerse).where(
        QuranVerse.sura_no == sura_no,
        QuranVerse.aya_no >= aya_start,
        QuranVerse.aya_no <= aya_end,
    ).order_by(QuranVerse.aya_no)

    if include_translations:
        query = query.options(selectinload(QuranVerse.translations))

    result = await session.execute(query)
    verses = result.scalars().all()

    if not verses:
        raise HTTPException(
            status_code=404, detail=f"Verses {sura_no}:{aya_start}-{aya_end} not found"
        )

    return [VerseResponse.model_validate(v) for v in verses]


@router.get("/page/{page_no}", response_model=List[VerseResponse])
async def get_page_verses(
    page_no: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get all verses on a specific page of the Mushaf.
    """
    if page_no < 1 or page_no > 604:
        raise HTTPException(status_code=400, detail="Page number must be between 1 and 604")

    query = (
        select(QuranVerse)
        .where(QuranVerse.page_no == page_no)
        .order_by(QuranVerse.id)
        .options(selectinload(QuranVerse.translations))
    )

    result = await session.execute(query)
    verses = result.scalars().all()

    if not verses:
        raise HTTPException(status_code=404, detail=f"Page {page_no} not found")

    return [VerseResponse.model_validate(v) for v in verses]


@router.get("/juz/{juz_no}", response_model=List[VerseResponse])
async def get_juz_verses(
    juz_no: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get verses for a specific juz (with pagination).
    """
    if juz_no < 1 or juz_no > 30:
        raise HTTPException(status_code=400, detail="Juz number must be between 1 and 30")

    query = (
        select(QuranVerse)
        .where(QuranVerse.juz_no == juz_no)
        .order_by(QuranVerse.id)
        .offset(offset)
        .limit(limit)
    )

    result = await session.execute(query)
    verses = result.scalars().all()

    return [VerseResponse.model_validate(v) for v in verses]


@router.get("/tafseer/{sura_no}/{aya_no}", response_model=List[TafseerChunkResponse])
async def get_verse_tafseer(
    sura_no: int,
    aya_no: int,
    sources: Optional[List[str]] = Query(None, description="Filter by source IDs"),
    language: Optional[str] = Query(None, description="Filter by language (ar/en)"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get tafseer for a specific verse.
    """
    # First get the verse ID
    verse_result = await session.execute(
        select(QuranVerse.id).where(
            QuranVerse.sura_no == sura_no,
            QuranVerse.aya_no == aya_no,
        )
    )
    verse_id = verse_result.scalar_one_or_none()

    if not verse_id:
        raise HTTPException(status_code=404, detail=f"Verse {sura_no}:{aya_no} not found")

    # Get tafseer chunks
    query = select(TafseerChunk).where(
        TafseerChunk.verse_start_id <= verse_id,
        TafseerChunk.verse_end_id >= verse_id,
    )

    if sources:
        query = query.where(TafseerChunk.source_id.in_(sources))

    result = await session.execute(query)
    chunks = result.scalars().all()

    # Filter by language if specified
    response = []
    for chunk in chunks:
        if language == "ar" and not chunk.content_ar:
            continue
        if language == "en" and not chunk.content_en:
            continue

        response.append(
            TafseerChunkResponse(
                chunk_id=chunk.chunk_id,
                source_id=chunk.source_id,
                verse_reference=chunk.verse_reference,
                content_ar=chunk.content_ar if language != "en" else None,
                content_en=chunk.content_en if language != "ar" else None,
                scholarly_consensus=chunk.scholarly_consensus,
            )
        )

    return response


@router.get("/tafseer/sources", response_model=List[dict])
async def get_tafseer_sources(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get available tafseer sources.
    """
    result = await session.execute(select(TafseerSource))
    sources = result.scalars().all()

    return [
        {
            "id": s.id,
            "name_ar": s.name_ar,
            "name_en": s.name_en,
            "author_en": s.author_en,
            "language": s.language,
            "methodology": s.methodology,
            "reliability_score": s.reliability_score,
        }
        for s in sources
    ]


@router.get("/search")
async def search_quran(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Search Quran text (simplified search, not full-text).
    """
    # Simple LIKE search on simplified text
    query = (
        select(QuranVerse)
        .where(QuranVerse.text_imlaei.ilike(f"%{q}%"))
        .limit(limit)
    )

    result = await session.execute(query)
    verses = result.scalars().all()

    return {
        "query": q,
        "count": len(verses),
        "results": [
            {
                "id": v.id,
                "reference": f"{v.sura_no}:{v.aya_no}",
                "sura_name": v.sura_name_en,
                "text": v.text_uthmani,
            }
            for v in verses
        ],
    }
