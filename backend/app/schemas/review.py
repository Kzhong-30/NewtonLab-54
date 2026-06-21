from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    script_id: int
    rating: int = Field(..., ge=1, le=5)
    content: Optional[str] = None
    is_spoiler: bool = False


class ReviewCreate(ReviewBase):
    game_id: Optional[int] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None
    is_spoiler: Optional[bool] = None


class Review(ReviewBase):
    id: int
    user_id: int
    game_id: Optional[int] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
