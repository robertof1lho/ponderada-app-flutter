from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GenerateAlterEgoRequest(BaseModel):
    selfie_url: str
    universe: str
    # user_id removed — derived from JWT claims


class AlterEgoResponse(BaseModel):
    id: str
    image_url: str
    universe: str
    created_at: Optional[datetime] = None
    username: Optional[str] = None

class FeedItem(BaseModel):
    alter_ego_id: str
    image_url: str
    universe: str
    created_at: datetime
    username: str

class SimilarUser(BaseModel):
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    shared_styles: int

class GenerateAlterEgoResponse(BaseModel):
    id: str
    image_url: str
