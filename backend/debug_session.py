import asyncio
import os
from bson import ObjectId
from app.database import get_db, connect_db, close_db
from app.config import settings

async def check_session(session_id_str):
    await connect_db()
    db = get_db()
    
    try:
        session_id = ObjectId(session_id_str)
        print(f"Checking for session ID: {session_id}")
        
        session = await db.coaching_sessions.find_one({"_id": session_id})
        
        if session:
            print(f"Session FOUND: {session_id}")
            print(f"Status: {session.get('status')}")
            print(f"Goal ID: {session.get('goal_id')}")
        else:
            print(f"Session NOT FOUND: {session_id}")
            
            # List all sessions to see what exists
            print("\nListing all sessions:")
            async for s in db.coaching_sessions.find():
                print(f"- {s['_id']} (Status: {s.get('status')}, Goal ID: {s.get('goal_id')})")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(check_session("699214393860e47e0ee82745"))
