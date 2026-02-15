"""
Database migration script to add formation tracking and coaching features.

This script adds:
- coaching_style and memories fields to users collection
- formation_count, is_formed, current_streak, best_streak fields to habits collection

Run this before deploying the new version:
    cd backend
    python migrations/add_formation_tracking.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def migrate():
    """Run database migration."""
    print("Starting database migration...")
    print(f"Connecting to: {settings.mongodb_url}")
    print(f"Database: {settings.database_name}")

    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    # Migrate users collection
    print("\n1. Migrating users collection...")
    users_result = await db.users.update_many(
        {"coaching_style": {"$exists": False}},
        {"$set": {"coaching_style": "balanced", "memories": []}}
    )
    print(f"   Updated {users_result.modified_count} users with default coaching_style and memories")

    # Migrate habits collection
    print("\n2. Migrating habits collection...")
    habits_result = await db.habits.update_many(
        {"formation_count": {"$exists": False}},
        {
            "$set": {
                "formation_count": 0,
                "is_formed": False,
                "current_streak": 0,
                "best_streak": 0
            }
        }
    )
    print(f"   Updated {habits_result.modified_count} habits with formation tracking fields")

    # Verify migration
    print("\n3. Verifying migration...")
    sample_user = await db.users.find_one({"coaching_style": {"$exists": True}})
    sample_habit = await db.habits.find_one({"formation_count": {"$exists": True}})

    if sample_user:
        print(f"   ✓ User sample: coaching_style={sample_user.get('coaching_style')}, "
              f"memories count={len(sample_user.get('memories', []))}")

    if sample_habit:
        print(f"   ✓ Habit sample: formation_count={sample_habit.get('formation_count')}, "
              f"is_formed={sample_habit.get('is_formed')}")

    print("\nMigration complete!")
    client.close()


if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
