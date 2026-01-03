"""
Story and connection models for Quranic narrative tracking.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.database import Base


class StoryCategory(str, Enum):
    """Categories of Quranic stories."""
    PROPHET = "prophet"
    NATION = "nation"
    PARABLE = "parable"
    HISTORICAL = "historical"
    UNSEEN = "unseen"  # Afterlife, angels, etc.


class ConnectionType(str, Enum):
    """Types of connections between story segments."""
    CONTINUATION = "continuation"  # Same story continues
    PARALLEL = "parallel"  # Similar theme/event
    CONTRAST = "contrast"  # Opposing lessons
    REFERENCE = "reference"  # Brief mention of detailed story
    EXPANSION = "expansion"  # Adds new details


class Theme(Base):
    """
    Quranic themes that appear across stories and verses.
    """
    __tablename__ = "themes"

    id = Column(String(50), primary_key=True)  # e.g., "tawakkul", "sabr"
    name_ar = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=False)

    # Hierarchy
    parent_theme_id = Column(String(50), ForeignKey("themes.id"), nullable=True)

    # Description
    description_ar = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)

    # Related themes (for graph)
    related_themes = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("Theme", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<Theme {self.id}: {self.name_en}>"


class Story(Base):
    """
    Quranic stories - major narratives mentioned in the Quran.
    """
    __tablename__ = "stories"

    id = Column(String(50), primary_key=True)  # e.g., "story_musa", "story_ibrahim"
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)

    category = Column(String(50), nullable=False)  # From StoryCategory enum

    # Main figures in the story
    main_figures = Column(ARRAY(String), nullable=True)  # ["Musa", "Firawn"]

    # Themes covered
    themes = Column(ARRAY(String), nullable=True)  # ["liberation", "miracles"]

    # Summary
    summary_ar = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)

    # Historical context
    timeline_era = Column(String(50), nullable=True)  # "ancient_egypt", "pre-islamic"

    # Lessons
    lessons_ar = Column(Text, nullable=True)
    lessons_en = Column(Text, nullable=True)

    # Metadata
    total_verses = Column(Integer, default=0)
    suras_mentioned = Column(ARRAY(Integer), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    segments = relationship("StorySegment", back_populates="story", lazy="selectin")

    def __repr__(self):
        return f"<Story {self.id}: {self.name_en}>"


class StorySegment(Base):
    """
    Story segments - portions of a story as they appear in different surahs.

    A story like Musa's appears in 27+ surahs, each segment captures
    a specific portion of the narrative in a specific location.
    """
    __tablename__ = "story_segments"

    id = Column(String(100), primary_key=True)  # e.g., "musa_birth_qasas"
    story_id = Column(String(50), ForeignKey("stories.id"), nullable=False, index=True)

    # Narrative position
    narrative_order = Column(Integer, nullable=False)  # Chronological order in the story
    segment_type = Column(String(50), nullable=True)  # "introduction", "development", "climax", "resolution"
    aspect = Column(String(100), nullable=True)  # What aspect is covered: "birth", "exile", "return"

    # Location in Quran
    sura_no = Column(Integer, nullable=False, index=True)
    aya_start = Column(Integer, nullable=False)
    aya_end = Column(Integer, nullable=False)

    # Verse IDs (for joining)
    verse_ids = Column(ARRAY(Integer), nullable=True)

    # Summary
    summary_ar = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)

    # Key points
    key_points_ar = Column(ARRAY(String), nullable=True)
    key_points_en = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    story = relationship("Story", back_populates="segments")

    __table_args__ = (
        Index("ix_segment_story", "story_id"),
        Index("ix_segment_location", "sura_no", "aya_start", "aya_end"),
    )

    def __repr__(self):
        return f"<StorySegment {self.id} ({self.sura_no}:{self.aya_start}-{self.aya_end})>"

    @property
    def verse_reference(self) -> str:
        """Get verse reference for this segment."""
        if self.aya_start == self.aya_end:
            return f"{self.sura_no}:{self.aya_start}"
        return f"{self.sura_no}:{self.aya_start}-{self.aya_end}"


class StoryConnection(Base):
    """
    Connections between story segments - tracks how parts of a story
    relate to each other across different surahs.

    IMPORTANT: Every connection MUST have at least one evidence_chunk_id
    to maintain scholarly grounding.
    """
    __tablename__ = "story_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Source and target segments
    source_segment_id = Column(
        String(100), ForeignKey("story_segments.id"), nullable=False, index=True
    )
    target_segment_id = Column(
        String(100), ForeignKey("story_segments.id"), nullable=False, index=True
    )

    # Connection metadata
    connection_type = Column(String(50), nullable=False)  # From ConnectionType enum
    strength = Column(Float, default=1.0)  # 0.0-1.0 relevance score

    # Explanation
    explanation_ar = Column(Text, nullable=True)
    explanation_en = Column(Text, nullable=True)

    # CRITICAL: Evidence from tafseer - at least one required
    evidence_chunk_ids = Column(ARRAY(String), nullable=False)

    # Themes linking these segments
    shared_themes = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source_segment = relationship("StorySegment", foreign_keys=[source_segment_id])
    target_segment = relationship("StorySegment", foreign_keys=[target_segment_id])

    __table_args__ = (
        # Ensure at least one evidence chunk is provided
        CheckConstraint(
            "array_length(evidence_chunk_ids, 1) >= 1",
            name="ck_connection_has_evidence"
        ),
        Index("ix_connection_source", "source_segment_id"),
        Index("ix_connection_target", "target_segment_id"),
    )

    def __repr__(self):
        return f"<StoryConnection {self.source_segment_id} -> {self.target_segment_id}>"
