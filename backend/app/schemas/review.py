from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    script_id: Optional[int] = None
    rating: float = Field(..., ge=1, le=5)
    content: Optional[str] = None
    is_anonymous: bool = False


class ReviewCreate(ReviewBase):
    game_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    content: Optional[str] = None
    is_anonymous: Optional[bool] = None


class Review(ReviewBase):
    id: int
    author_id: int
    target_user_id: Optional[int] = None
    game_id: Optional[int] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
