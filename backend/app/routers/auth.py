from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel

from app.config import settings
from app.auth.jwt import create_access_token
from app.database import get_db
from app.utils.dates import now

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    credential: str


@router.post("/google")
async def google_login(data: GoogleLoginRequest):
    try:
        idinfo = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_id = idinfo["sub"]
    email = idinfo.get("email", "")
    name = idinfo.get("name", "")
    picture = idinfo.get("picture", "")

    db = get_db()

    # Check if user is admin
    admin_emails = [e.strip() for e in settings.admin_emails.split(",") if e.strip()]
    is_admin = email in admin_emails

    # Upsert user
    user = await db.users.find_one({"google_id": google_id})
    if user:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"name": name, "picture": picture, "is_admin": is_admin, "updated_at": now()}},
        )
        user_id = str(user["_id"])
    else:
        user_doc = {
            "google_id": google_id,
            "email": email,
            "name": name,
            "picture": picture,
            "is_admin": is_admin,
            "created_at": now(),
            "updated_at": now(),
        }
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

    token = create_access_token({"sub": user_id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "is_admin": is_admin,
        },
    }
