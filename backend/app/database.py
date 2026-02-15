from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    await create_indexes()


async def close_db():
    global client
    if client:
        client.close()


async def create_indexes():
    await db.daily_logs.create_index(
        [("user_id", 1), ("goal_id", 1), ("date", 1)], unique=True
    )
    await db.habits.create_index([("goal_id", 1), ("status", 1)])
    await db.trackers.create_index([("goal_id", 1)])
    await db.coaching_sessions.create_index([("goal_id", 1), ("status", 1)])
    await db.users.create_index([("google_id", 1)], unique=True)


def get_db() -> AsyncIOMotorDatabase:
    return db
