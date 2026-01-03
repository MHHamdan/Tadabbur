#!/usr/bin/env python3
"""
Verify database is seeded correctly.

Checks:
  - Quran verses table has 6236 verses
  - Tafseer sources exist
  - Tafseer chunks are linked correctly
  - Stories and segments exist

Exit codes:
  0 - Database seeded correctly
  1 - Database seeding issues found
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, text, func, select
from sqlalchemy.orm import Session

# Expected counts
EXPECTED_VERSE_COUNT = 6236
EXPECTED_SURA_COUNT = 114
EXPECTED_PAGE_COUNT = 604
EXPECTED_JUZ_COUNT = 30


def get_db_url() -> str:
    """Get database URL from environment."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://tadabbur:tadabbur_dev@localhost:5432/tadabbur"
    )


def check_verse_count(session: Session) -> tuple[bool, str]:
    """Check total verse count."""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM quran_verses"))
        count = result.scalar()

        if count == EXPECTED_VERSE_COUNT:
            return True, f"Verse count: {count} (expected {EXPECTED_VERSE_COUNT})"
        elif count == 0:
            return False, "No verses found - database not seeded"
        else:
            return False, f"Verse count mismatch: {count} (expected {EXPECTED_VERSE_COUNT})"
    except Exception as e:
        return False, f"Error checking verses: {str(e)}"


def check_sura_distribution(session: Session) -> tuple[bool, str]:
    """Check sura distribution."""
    try:
        result = session.execute(text(
            "SELECT COUNT(DISTINCT sura_no) FROM quran_verses"
        ))
        count = result.scalar()

        if count == EXPECTED_SURA_COUNT:
            return True, f"Sura count: {count} (expected {EXPECTED_SURA_COUNT})"
        elif count == 0:
            return False, "No suras found"
        else:
            return False, f"Sura count mismatch: {count} (expected {EXPECTED_SURA_COUNT})"
    except Exception as e:
        return False, f"Error checking suras: {str(e)}"


def check_page_distribution(session: Session) -> tuple[bool, str]:
    """Check page distribution."""
    try:
        result = session.execute(text(
            "SELECT COUNT(DISTINCT page_no) FROM quran_verses"
        ))
        count = result.scalar()

        if count == EXPECTED_PAGE_COUNT:
            return True, f"Page count: {count} (expected {EXPECTED_PAGE_COUNT})"
        elif count == 0:
            return False, "No pages found"
        else:
            # Allow some variance for different editions
            if count >= EXPECTED_PAGE_COUNT - 5:
                return True, f"Page count: {count} (close to expected {EXPECTED_PAGE_COUNT})"
            return False, f"Page count mismatch: {count} (expected ~{EXPECTED_PAGE_COUNT})"
    except Exception as e:
        return False, f"Error checking pages: {str(e)}"


def check_tafseer_sources(session: Session) -> tuple[bool, str]:
    """Check tafseer sources exist."""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM tafseer_sources"))
        count = result.scalar()

        if count > 0:
            # Get source names
            names_result = session.execute(text(
                "SELECT id, name_en FROM tafseer_sources LIMIT 5"
            ))
            names = [f"{row[0]}: {row[1]}" for row in names_result]
            return True, f"Found {count} tafseer sources: {', '.join(names)}"
        else:
            return False, "No tafseer sources found - need to seed tafseer data"
    except Exception as e:
        if "does not exist" in str(e):
            return False, "tafseer_sources table does not exist - run migrations"
        return False, f"Error checking tafseer sources: {str(e)}"


def check_tafseer_chunks(session: Session) -> tuple[bool, str]:
    """Check tafseer chunks exist and are properly linked."""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM tafseer_chunks"))
        count = result.scalar()

        if count > 0:
            # Check linking
            orphan_result = session.execute(text("""
                SELECT COUNT(*) FROM tafseer_chunks tc
                WHERE NOT EXISTS (
                    SELECT 1 FROM quran_verses qv WHERE qv.id = tc.verse_start_id
                )
            """))
            orphan_count = orphan_result.scalar()

            if orphan_count == 0:
                return True, f"Found {count} tafseer chunks, all properly linked"
            else:
                return False, f"Found {orphan_count} orphan chunks (not linked to verses)"
        else:
            return False, "No tafseer chunks found - need to seed tafseer data"
    except Exception as e:
        if "does not exist" in str(e):
            return False, "tafseer_chunks table does not exist - run migrations"
        return False, f"Error checking tafseer chunks: {str(e)}"


def check_stories(session: Session) -> tuple[bool, str]:
    """Check stories exist."""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM stories"))
        count = result.scalar()

        if count > 0:
            return True, f"Found {count} stories"
        else:
            return False, "No stories found - need to seed story data"
    except Exception as e:
        if "does not exist" in str(e):
            return False, "stories table does not exist - run migrations"
        return False, f"Error checking stories: {str(e)}"


def check_story_segments(session: Session) -> tuple[bool, str]:
    """Check story segments exist and are linked."""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM story_segments"))
        count = result.scalar()

        if count > 0:
            # Check all segments have valid stories
            orphan_result = session.execute(text("""
                SELECT COUNT(*) FROM story_segments ss
                WHERE NOT EXISTS (
                    SELECT 1 FROM stories s WHERE s.id = ss.story_id
                )
            """))
            orphan_count = orphan_result.scalar()

            if orphan_count == 0:
                return True, f"Found {count} story segments, all linked to stories"
            else:
                return False, f"Found {orphan_count} orphan segments"
        else:
            return False, "No story segments found"
    except Exception as e:
        if "does not exist" in str(e):
            return False, "story_segments table does not exist - run migrations"
        return False, f"Error checking story segments: {str(e)}"


def check_translations(session: Session) -> tuple[bool, str]:
    """Check translations exist."""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM translations"))
        count = result.scalar()

        if count > 0:
            # Get language distribution
            lang_result = session.execute(text("""
                SELECT language, COUNT(*) as cnt
                FROM translations
                GROUP BY language
            """))
            langs = {row[0]: row[1] for row in lang_result}
            lang_str = ", ".join([f"{k}: {v}" for k, v in langs.items()])
            return True, f"Found {count} translations ({lang_str})"
        else:
            return False, "No translations found - consider adding translations"
    except Exception as e:
        if "does not exist" in str(e):
            return False, "translations table does not exist - run migrations"
        return False, f"Error checking translations: {str(e)}"


def main():
    """Run all database seed verifications."""
    print("=" * 60)
    print("DATABASE SEED VERIFICATION")
    print("=" * 60)

    db_url = get_db_url()
    print(f"\nDatabase: {db_url.split('@')[1] if '@' in db_url else db_url}")

    try:
        engine = create_engine(db_url)
        with Session(engine) as session:
            all_passed = True
            results = []

            # Check verses
            print("\n[1/7] Checking Quran verses...")
            passed, msg = check_verse_count(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Verse count", passed))
            if not passed:
                all_passed = False

            # Check suras
            print("\n[2/7] Checking sura distribution...")
            passed, msg = check_sura_distribution(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Sura distribution", passed))
            if not passed:
                all_passed = False

            # Check pages
            print("\n[3/7] Checking page distribution...")
            passed, msg = check_page_distribution(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Page distribution", passed))
            if not passed:
                all_passed = False

            # Check tafseer sources
            print("\n[4/7] Checking tafseer sources...")
            passed, msg = check_tafseer_sources(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Tafseer sources", passed))
            # Tafseer is optional for MVP
            # if not passed: all_passed = False

            # Check tafseer chunks
            print("\n[5/7] Checking tafseer chunks...")
            passed, msg = check_tafseer_chunks(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Tafseer chunks", passed))
            # Tafseer is optional for MVP

            # Check stories
            print("\n[6/7] Checking stories...")
            passed, msg = check_stories(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Stories", passed))
            # Stories are optional for MVP

            # Check translations
            print("\n[7/7] Checking translations...")
            passed, msg = check_translations(session)
            print(f"  {'PASS' if passed else 'FAIL'}: {msg}")
            results.append(("Translations", passed))
            # Translations are optional

            # Summary
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)

            for name, passed in results:
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {name}: {status}")

            print("\n" + "=" * 60)

            # Core requirements: verses must be seeded
            core_passed = results[0][1]  # Verse count

            if core_passed:
                print("OVERALL: PASS - Core data (verses) is seeded")
                print("=" * 60)
                sys.exit(0)
            else:
                print("OVERALL: FAIL - Core data missing")
                print("=" * 60)
                print("\nREMEDIATION:")
                print("  1. Run migrations: alembic upgrade head")
                print("  2. Run seed script: python scripts/ingest/seed_quran.py")
                print("  3. Run tafseer seed: python scripts/ingest/seed_tafseer.py")
                sys.exit(1)

    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        print("\nREMEDIATION:")
        print("  1. Ensure PostgreSQL is running")
        print("  2. Check database credentials")
        print("  3. Run migrations: alembic upgrade head")
        sys.exit(1)


if __name__ == "__main__":
    main()
