"""
Stories API routes for Quranic narratives and connections.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_async_session
from app.models.story import Story, StorySegment, StoryConnection, Theme

router = APIRouter()


# Pydantic schemas
class SegmentResponse(BaseModel):
    """Story segment response."""
    id: str
    narrative_order: int
    segment_type: Optional[str]
    aspect: Optional[str]
    sura_no: int
    aya_start: int
    aya_end: int
    verse_reference: str
    summary_ar: Optional[str]
    summary_en: Optional[str]

    class Config:
        from_attributes = True


class ConnectionResponse(BaseModel):
    """Story connection response."""
    id: int
    source_segment_id: str
    target_segment_id: str
    connection_type: str
    strength: float
    explanation_ar: Optional[str]
    explanation_en: Optional[str]
    evidence_chunk_ids: List[str]
    shared_themes: Optional[List[str]]

    class Config:
        from_attributes = True


class StoryResponse(BaseModel):
    """Story response schema."""
    id: str
    name_ar: str
    name_en: str
    category: str
    main_figures: Optional[List[str]]
    themes: Optional[List[str]]
    summary_ar: Optional[str]
    summary_en: Optional[str]
    total_verses: int
    suras_mentioned: Optional[List[int]]

    class Config:
        from_attributes = True


class StoryDetailResponse(StoryResponse):
    """Story with segments."""
    segments: List[SegmentResponse] = []


class ThemeResponse(BaseModel):
    """Theme response schema."""
    id: str
    name_ar: str
    name_en: str
    description_ar: Optional[str]
    description_en: Optional[str]
    parent_theme_id: Optional[str]
    related_themes: Optional[List[str]]

    class Config:
        from_attributes = True


class StoryGraphNode(BaseModel):
    """Node in the story graph."""
    id: str
    type: str  # "story", "segment", "verse"
    label: str
    data: dict


class StoryGraphEdge(BaseModel):
    """Edge in the story graph."""
    source: str
    target: str
    type: str
    label: Optional[str]


class StoryGraphResponse(BaseModel):
    """Story graph data for visualization."""
    nodes: List[StoryGraphNode]
    edges: List[StoryGraphEdge]


# Routes
@router.get("/", response_model=List[StoryResponse])
async def list_stories(
    category: Optional[str] = Query(None, description="Filter by category"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all Quranic stories with optional filtering.
    """
    query = select(Story).order_by(Story.name_en)

    if category:
        query = query.where(Story.category == category)

    if theme:
        query = query.where(Story.themes.contains([theme]))

    result = await session.execute(query)
    stories = result.scalars().all()

    return [StoryResponse.model_validate(s) for s in stories]


@router.get("/categories")
async def get_story_categories():
    """
    Get available story categories.
    """
    return {
        "categories": [
            {"id": "prophet", "name_en": "Prophet Stories", "name_ar": "قصص الأنبياء"},
            {"id": "nation", "name_en": "Nation Stories", "name_ar": "قصص الأمم"},
            {"id": "parable", "name_en": "Parables", "name_ar": "الأمثال"},
            {"id": "historical", "name_en": "Historical Events", "name_ar": "الأحداث التاريخية"},
            {"id": "unseen", "name_en": "The Unseen", "name_ar": "الغيب"},
        ]
    }


@router.get("/themes", response_model=List[ThemeResponse])
async def list_themes(
    parent_id: Optional[str] = Query(None, description="Filter by parent theme"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all themes.
    """
    query = select(Theme).order_by(Theme.name_en)

    if parent_id:
        query = query.where(Theme.parent_theme_id == parent_id)

    result = await session.execute(query)
    themes = result.scalars().all()

    return [ThemeResponse.model_validate(t) for t in themes]


@router.get("/{story_id}", response_model=StoryDetailResponse)
async def get_story(
    story_id: str,
    include_segments: bool = Query(True),
    language: Optional[str] = Query(None, description="ar or en"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific story with its segments.
    """
    query = select(Story).where(Story.id == story_id)

    if include_segments:
        query = query.options(selectinload(Story.segments))

    result = await session.execute(query)
    story = result.scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")

    response = StoryDetailResponse.model_validate(story)

    # Sort segments by narrative order
    if story.segments:
        response.segments = sorted(
            [SegmentResponse.model_validate(s) for s in story.segments],
            key=lambda x: x.narrative_order,
        )

    return response


@router.get("/{story_id}/connections", response_model=List[ConnectionResponse])
async def get_story_connections(
    story_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get all connections for a story's segments.
    """
    # First get all segment IDs for this story
    segment_result = await session.execute(
        select(StorySegment.id).where(StorySegment.story_id == story_id)
    )
    segment_ids = [row[0] for row in segment_result.all()]

    if not segment_ids:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")

    # Get connections where source or target is in this story
    query = select(StoryConnection).where(
        (StoryConnection.source_segment_id.in_(segment_ids))
        | (StoryConnection.target_segment_id.in_(segment_ids))
    )

    result = await session.execute(query)
    connections = result.scalars().all()

    return [ConnectionResponse.model_validate(c) for c in connections]


@router.get("/{story_id}/graph", response_model=StoryGraphResponse)
async def get_story_graph(
    story_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get story as a graph structure for visualization.

    Returns nodes (segments) and edges (connections) suitable for
    graph visualization libraries like Cytoscape.js.
    """
    # Get story with segments
    story_result = await session.execute(
        select(Story)
        .where(Story.id == story_id)
        .options(selectinload(Story.segments))
    )
    story = story_result.scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")

    nodes = []
    edges = []

    # Add story node
    nodes.append(
        StoryGraphNode(
            id=story.id,
            type="story",
            label=story.name_en,
            data={
                "name_ar": story.name_ar,
                "category": story.category,
                "themes": story.themes or [],
            },
        )
    )

    # Add segment nodes
    segment_ids = []
    for segment in story.segments:
        segment_ids.append(segment.id)
        nodes.append(
            StoryGraphNode(
                id=segment.id,
                type="segment",
                label=f"{segment.sura_no}:{segment.aya_start}-{segment.aya_end}",
                data={
                    "narrative_order": segment.narrative_order,
                    "aspect": segment.aspect,
                    "summary_en": segment.summary_en,
                    "summary_ar": segment.summary_ar,
                },
            )
        )
        # Edge from story to segment
        edges.append(
            StoryGraphEdge(
                source=story.id,
                target=segment.id,
                type="contains",
                label=None,
            )
        )

    # Get connections between segments
    if segment_ids:
        conn_result = await session.execute(
            select(StoryConnection).where(
                StoryConnection.source_segment_id.in_(segment_ids)
            )
        )
        connections = conn_result.scalars().all()

        for conn in connections:
            edges.append(
                StoryGraphEdge(
                    source=conn.source_segment_id,
                    target=conn.target_segment_id,
                    type=conn.connection_type,
                    label=conn.connection_type.replace("_", " ").title(),
                )
            )

    return StoryGraphResponse(nodes=nodes, edges=edges)


@router.get("/by-figure/{figure}")
async def get_stories_by_figure(
    figure: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get stories featuring a specific figure (prophet, king, etc.).
    """
    query = select(Story).where(Story.main_figures.contains([figure]))
    result = await session.execute(query)
    stories = result.scalars().all()

    return {
        "figure": figure,
        "count": len(stories),
        "stories": [StoryResponse.model_validate(s) for s in stories],
    }


@router.get("/by-sura/{sura_no}")
async def get_stories_in_sura(
    sura_no: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get all story segments that appear in a specific sura.
    """
    if sura_no < 1 or sura_no > 114:
        raise HTTPException(status_code=400, detail="Sura must be between 1 and 114")

    query = (
        select(StorySegment)
        .where(StorySegment.sura_no == sura_no)
        .order_by(StorySegment.aya_start)
    )
    result = await session.execute(query)
    segments = result.scalars().all()

    # Group by story
    story_map = {}
    for seg in segments:
        if seg.story_id not in story_map:
            story_map[seg.story_id] = []
        story_map[seg.story_id].append(SegmentResponse.model_validate(seg))

    return {
        "sura_no": sura_no,
        "stories": story_map,
    }
