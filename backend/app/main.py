from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_db, close_db
from app.routers import auth, goals, habits, trackers, daily_logs, coaching, models, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="Kairos", description="Adaptive AI Coaching", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(habits.router)
app.include_router(trackers.router)
app.include_router(daily_logs.router)
app.include_router(coaching.router)
app.include_router(models.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
