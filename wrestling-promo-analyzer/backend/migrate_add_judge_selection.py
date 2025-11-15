"""
Migration: Add selected_judge_slug field to videos table

This migration adds support for multi-judge selection by adding the
selected_judge_slug field to the videos table.

Run this script once to migrate existing database:
    python migrate_add_judge_selection.py
"""

from sqlalchemy import text
from database import SessionLocal, engine


def migrate():
    """Add selected_judge_slug column to videos table"""

    print("=" * 70)
    print("MIGRATION: Add selected_judge_slug to videos table")
    print("=" * 70)

    db = SessionLocal()

    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'videos'
            AND column_name = 'selected_judge_slug'
        """))

        if result.fetchone():
            print("✅ Column 'selected_judge_slug' already exists. No migration needed.")
            return

        print("Adding 'selected_judge_slug' column to videos table...")

        # Add the column with default value
        db.execute(text("""
            ALTER TABLE videos
            ADD COLUMN selected_judge_slug VARCHAR(50) DEFAULT 'jake-morrison'
        """))

        db.commit()

        print("✅ Migration successful!")
        print("   - Added column: selected_judge_slug VARCHAR(50)")
        print("   - Default value: 'jake-morrison'")

        # Verify the migration
        result = db.execute(text("""
            SELECT COUNT(*) FROM videos WHERE selected_judge_slug = 'jake-morrison'
        """))
        count = result.scalar()

        print(f"   - Verified: {count} existing videos now have default judge")

    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        print("\nIf the table doesn't exist yet, run:")
        print("    python -c 'from database import init_db; init_db()'")
        raise

    finally:
        db.close()

    print("=" * 70)


def rollback():
    """Remove selected_judge_slug column (rollback migration)"""

    print("=" * 70)
    print("ROLLBACK: Remove selected_judge_slug from videos table")
    print("=" * 70)

    db = SessionLocal()

    try:
        print("Removing 'selected_judge_slug' column...")

        db.execute(text("""
            ALTER TABLE videos
            DROP COLUMN IF EXISTS selected_judge_slug
        """))

        db.commit()

        print("✅ Rollback successful!")

    except Exception as e:
        db.rollback()
        print(f"❌ Rollback failed: {e}")
        raise

    finally:
        db.close()

    print("=" * 70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
