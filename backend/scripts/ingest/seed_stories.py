#!/usr/bin/env python3
"""
Seed Quranic stories from manifest.

This script:
1. Reads the stories.json manifest
2. Creates stories, segments, themes, and connections
3. Links segments to verse ranges
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.story import Story, StorySegment, Theme, StoryConnection
from app.models.quran import QuranVerse
from app.models.audit import AuditLog

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
MANIFESTS_DIR = PROJECT_ROOT / "data" / "manifests"


def get_db_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql://tadabbur:tadabbur_dev@localhost:5432/tadabbur")


def load_manifest() -> dict:
    manifest_path = MANIFESTS_DIR / "stories.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_verse_ids_for_range(session: Session, sura_no: int, aya_start: int, aya_end: int) -> list:
    """Get verse IDs for a sura/aya range."""
    result = session.execute(
        select(QuranVerse.id).where(
            QuranVerse.sura_no == sura_no,
            QuranVerse.aya_no >= aya_start,
            QuranVerse.aya_no <= aya_end,
        ).order_by(QuranVerse.aya_no)
    )
    return [row[0] for row in result.all()]


def seed_themes(session: Session, themes: list) -> int:
    """Seed themes."""
    count = 0
    for theme_data in themes:
        theme = Theme(
            id=theme_data["id"],
            name_ar=theme_data["name_ar"],
            name_en=theme_data["name_en"],
            description_ar=theme_data.get("description_ar"),
            description_en=theme_data.get("description_en"),
            created_at=datetime.utcnow(),
        )
        session.merge(theme)
        count += 1
    session.commit()
    return count


def seed_stories(session: Session, stories: list) -> tuple[int, int]:
    """Seed stories and segments."""
    story_count = 0
    segment_count = 0

    for story_data in stories:
        # Create story
        story = Story(
            id=story_data["id"],
            name_ar=story_data["name_ar"],
            name_en=story_data["name_en"],
            category=story_data["category"],
            main_figures=story_data.get("main_figures"),
            themes=story_data.get("themes"),
            summary_ar=story_data.get("summary_ar"),
            summary_en=story_data.get("summary_en"),
            suras_mentioned=story_data.get("suras_mentioned"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.merge(story)
        story_count += 1

        # Create segments
        for seg_data in story_data.get("segments", []):
            verse_ids = get_verse_ids_for_range(
                session,
                seg_data["sura_no"],
                seg_data["aya_start"],
                seg_data["aya_end"],
            )

            segment = StorySegment(
                id=seg_data["id"],
                story_id=story_data["id"],
                narrative_order=seg_data["narrative_order"],
                segment_type=seg_data.get("segment_type"),
                aspect=seg_data.get("aspect"),
                sura_no=seg_data["sura_no"],
                aya_start=seg_data["aya_start"],
                aya_end=seg_data["aya_end"],
                verse_ids=verse_ids if verse_ids else None,
                summary_ar=seg_data.get("summary_ar"),
                summary_en=seg_data.get("summary_en"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.merge(segment)
            segment_count += 1

        session.commit()

    return story_count, segment_count


def main():
    print("=" * 60)
    print("STORIES SEEDING")
    print("=" * 60)

    start_time = datetime.now()

    try:
        print("\n[1/3] Loading manifest...")
        manifest = load_manifest()
        print(f"  Found {len(manifest.get('stories', []))} stories")
        print(f"  Found {len(manifest.get('themes', []))} themes")

        print("\n[2/3] Connecting to database...")
        engine = create_engine(get_db_url())

        with Session(engine) as session:
            # Check if verses exist
            verse_count = session.execute(select(QuranVerse.id).limit(1)).first()
            if not verse_count:
                print("  WARNING: No verses found. Run seed_quran.py first.")

            print("\n[3/3] Seeding data...")

            # Seed themes
            theme_count = seed_themes(session, manifest.get("themes", []))
            print(f"  Seeded {theme_count} themes")

            # Seed stories
            story_count, segment_count = seed_stories(session, manifest.get("stories", []))
            print(f"  Seeded {story_count} stories with {segment_count} segments")

            # Audit log
            AuditLog.log(
                session,
                action="data_import",
                actor="pipeline",
                entity_type="story",
                message=f"Seeded {story_count} stories, {segment_count} segments",
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
            )
            session.commit()

        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 60)
        print(f"SUCCESS: Seeding complete in {duration:.2f}s")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
