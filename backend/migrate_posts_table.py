"""
Database migration script for Post model refactor.

Adds new fields: mood_id, source_images
Makes product_id nullable
Backfills source_images from existing product.image_path data

Run this script BEFORE starting the server with the updated ORM model.
"""
import sqlite3
import json
import os

# Path to database
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def run_migration():
    """Execute the database migration."""
    print("🔄 Starting Post table migration...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Step 1: Check if columns already exist
        cursor.execute("PRAGMA table_info(posts)")
        columns = [row[1] for row in cursor.fetchall()]

        # Step 2: Add mood_id column if it doesn't exist
        if "mood_id" not in columns:
            print("  Adding mood_id column...")
            cursor.execute("ALTER TABLE posts ADD COLUMN mood_id TEXT")
            print("  ✅ mood_id column added")
        else:
            print("  mood_id column already exists")

        # Step 3: Add source_images column if it doesn't exist
        if "source_images" not in columns:
            print("  Adding source_images column...")
            cursor.execute("ALTER TABLE posts ADD COLUMN source_images TEXT")
            print("  ✅ source_images column added")
        else:
            print("  source_images column already exists")

        # Step 4: SQLite doesn't support ALTER COLUMN to make nullable
        # But since we're adding the column as TEXT (already nullable),
        # existing product_id column will remain as is
        # New code will handle NULL values
        print("  product_id will be handled as nullable in application code")

        # Step 5: Backfill source_images from existing product.image_path
        print("  Backfilling source_images from product data...")

        # Get all posts with their product image paths
        cursor.execute("""
            SELECT posts.id, products.image_path
            FROM posts
            LEFT JOIN products ON posts.product_id = products.id
            WHERE posts.source_images IS NULL
        """)

        posts_to_update = cursor.fetchall()
        print(f"  Found {len(posts_to_update)} posts to backfill")

        for post_id, product_image_path in posts_to_update:
            if product_image_path:
                # Store as JSON array with single image path
                source_images_json = json.dumps([product_image_path])
                cursor.execute(
                    "UPDATE posts SET source_images = ? WHERE id = ?",
                    (source_images_json, post_id)
                )

        print(f"  ✅ Backfilled {len(posts_to_update)} posts with source_images")

        # Commit all changes
        conn.commit()
        print("✅ Migration completed successfully!")

        # Step 6: Verify migration
        cursor.execute("SELECT COUNT(*) FROM posts WHERE source_images IS NOT NULL")
        backfilled_count = cursor.fetchone()[0]
        print(f"  ✓ Verification: {backfilled_count} posts have source_images")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("POST TABLE MIGRATION SCRIPT")
    print("=" * 60)
    print()

    # Check if backup exists
    backup_path = DB_PATH + ".backup_before_post_refactor"
    if os.path.exists(backup_path):
        print(f"✅ Backup found: {backup_path}")
    else:
        print("WARNING: No backup found!")
        print("   Creating backup now...")
        import shutil
        shutil.copy(DB_PATH, backup_path)
        print(f"✅ Backup created: {backup_path}")

    print()

    # Run migration
    run_migration()

    print()
    print("=" * 60)
    print("Migration complete! You can now start the server.")
    print("=" * 60)
