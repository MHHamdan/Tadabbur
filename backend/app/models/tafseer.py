"""
Tafseer source and chunk models.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.database import Base


class TafseerSource(Base):
    """
    Tafseer source metadata - tracks different tafseer books/authors.

    Examples: Ibn Kathir, Al-Tabari, Al-Qurtubi, Al-Sa'di
    """
    __tablename__ = "tafseer_sources"

    id = Column(String(50), primary_key=True)  # e.g., "ibn_kathir", "tabari"
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)

    # Author information
    author_ar = Column(String(200), nullable=True)
    author_en = Column(String(200), nullable=True)
    era = Column(String(50), nullable=True)  # "classical", "modern"
    death_year_hijri = Column(Integer, nullable=True)

    # Methodology
    methodology = Column(String(50), nullable=True)  # "bil_mathur", "bil_ray", "mixed"

    # Language and version
    language = Column(String(10), nullable=False)  # "ar", "en"
    version = Column(String(50), nullable=True)
    source_url = Column(Text, nullable=True)

    # Licensing
    license = Column(String(200), nullable=True)
    license_url = Column(Text, nullable=True)

    # Quality indicators
    reliability_score = Column(Float, default=1.0)  # 0.0-1.0 scholarly consensus
    is_primary_source = Column(Integer, default=1)  # 1=primary, 0=secondary

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chunks = relationship("TafseerChunk", back_populates="source", lazy="dynamic")

    def __repr__(self):
        return f"<TafseerSource {self.id} ({self.language})>"


class TafseerChunk(Base):
    """
    Tafseer content chunks - stores segmented tafseer content.

    Each chunk is linked to a verse range and contains searchable content.
    Used for RAG retrieval and must have a unique chunk_id for citation.
    """
    __tablename__ = "tafseer_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_id = Column(String(100), nullable=False, unique=True, index=True)  # Unique ID for citations

    source_id = Column(String(50), ForeignKey("tafseer_sources.id"), nullable=False, index=True)

    # Verse range this chunk explains
    verse_start_id = Column(Integer, ForeignKey("quran_verses.id"), nullable=False)
    verse_end_id = Column(Integer, ForeignKey("quran_verses.id"), nullable=False)

    # Alternative reference (for convenience)
    sura_no = Column(Integer, nullable=False, index=True)
    aya_start = Column(Integer, nullable=False)
    aya_end = Column(Integer, nullable=False)

    # Content
    content_ar = Column(Text, nullable=True)
    content_en = Column(Text, nullable=True)

    # Topics and themes covered
    topics = Column(ARRAY(String), nullable=True)

    # Scholarly consensus indicator
    scholarly_consensus = Column(String(50), nullable=True)  # "agreed", "majority", "disputed"

    # Chunk metadata
    chunk_order = Column(Integer, default=0)  # Order within the verse explanation
    word_count = Column(Integer, nullable=True)
    char_count = Column(Integer, nullable=True)

    # Embedding status
    is_embedded = Column(Integer, default=0)  # 0=not embedded, 1=embedded
    embedding_model = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    source = relationship("TafseerSource", back_populates="chunks")
    verse_start = relationship("QuranVerse", foreign_keys=[verse_start_id])
    verse_end = relationship("QuranVerse", foreign_keys=[verse_end_id])

    __table_args__ = (
        Index("ix_chunk_source", "source_id"),
        Index("ix_chunk_verse_range", "verse_start_id", "verse_end_id"),
        Index("ix_chunk_sura", "sura_no"),
    )

    def __repr__(self):
        return f"<TafseerChunk {self.chunk_id} ({self.source_id})>"

    @property
    def verse_reference(self) -> str:
        """Get verse reference for this chunk."""
        if self.aya_start == self.aya_end:
            return f"{self.sura_no}:{self.aya_start}"
        return f"{self.sura_no}:{self.aya_start}-{self.aya_end}"

    @property
    def citation(self) -> str:
        """Get citation string for this chunk."""
        return f"[{self.source_id}, {self.verse_reference}]"
