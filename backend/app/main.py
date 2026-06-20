from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.handlers.alter_ego_handler import router as alter_ego_router
from app.handlers.feed_handler import router as feed_router
from app.handlers.profile_handler import router as profile_router

app = FastAPI(title="AlterMe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alter_ego_router, prefix="/alter-ego", tags=["alter-ego"])
app.include_router(feed_router, prefix="/feed", tags=["feed"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])
