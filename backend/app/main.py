from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.handlers.auth_handler import router as auth_router
from app.handlers.alter_ego_handler import router as alter_ego_router
from app.handlers.feed_handler import router as feed_router
from app.handlers.upload_handler import router as upload_router

app = FastAPI(title="AlterMe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(upload_router, prefix="/upload", tags=["upload"])
app.include_router(alter_ego_router, prefix="/alter-ego", tags=["alter-ego"])
app.include_router(feed_router, prefix="/feed", tags=["feed"])
