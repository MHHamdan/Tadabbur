"""
Type definitions for RAG pipeline.
"""
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field


class QueryIntent(str, Enum):
    """Types of queries the RAG can handle."""
    VERSE_MEANING = "verse_meaning"
    STORY_EXPLORATION = "story_exploration"
    THEME_SEARCH = "theme_search"
    COMPARATIVE = "comparative"
    LINGUISTIC = "linguistic"
    RULING = "ruling"  # Fiqh-related (informational only)
    UNKNOWN = "unknown"


@dataclass
class RetrievedChunk:
    """A retrieved tafseer chunk with metadata."""
    chunk_id: str
    source_id: str
    source_name: str
    source_name_ar: str
    verse_reference: str
    sura_no: int
    aya_start: int
    aya_end: int
    content: str  # Content in requested language
    content_ar: Optional[str] = None
    content_en: Optional[str] = None
    relevance_score: float = 0.0
    scholarly_consensus: Optional[str] = None


@dataclass
class Citation:
    """Citation in a grounded response."""
    chunk_id: str
    source_id: str
    source_name: str
    verse_reference: str
    excerpt: str
    relevance_score: float


@dataclass
class GroundedResponse:
    """Response from RAG pipeline with mandatory citations."""
    answer: str
    citations: List[Citation]
    confidence: float
    scholarly_consensus: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)
    intent: str = "unknown"
    processing_time_ms: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "answer": self.answer,
            "citations": [
                {
                    "chunk_id": c.chunk_id,
                    "source_id": c.source_id,
                    "source_name": c.source_name,
                    "verse_reference": c.verse_reference,
                    "excerpt": c.excerpt,
                    "relevance_score": c.relevance_score,
                }
                for c in self.citations
            ],
            "confidence": self.confidence,
            "scholarly_consensus": self.scholarly_consensus,
            "warnings": self.warnings,
            "related_queries": self.related_queries,
            "intent": self.intent,
            "processing_time_ms": self.processing_time_ms,
        }


@dataclass
class ValidationResult:
    """Result of citation validation."""
    is_valid: bool
    valid_citations: List[str]
    invalid_citations: List[str]
    missing_citations: List[str]
    coverage_score: float  # 0.0-1.0


# Safe refusal responses
SAFE_REFUSAL_INSUFFICIENT = (
    "This requires further scholarly consultation based on available sources. "
    "The retrieved evidence is insufficient to provide a complete answer."
)

SAFE_REFUSAL_NO_SOURCES = (
    "I could not find relevant sources to answer this question. "
    "Please consult qualified scholars for guidance."
)

SAFE_REFUSAL_FIQH = (
    "Note: This information is provided for educational purposes only and "
    "should not be taken as a religious ruling (fatwa). Please consult "
    "qualified scholars for personal religious guidance."
)
