from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from ..models import PostType


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None


class Comment(CommentBase):
    id: int
    post_id: int
    author_id: Optional[int] = None
    username: Optional[str] = None
    author_name: Optional[str] = None
    avatar: Optional[str] = None
    parent_id: Optional[int] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommunityPostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    post_type: PostType = PostType.RECOMMENDATION
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    script_id: Optional[int] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_spoiler: bool = False


class CommunityPostCreate(CommunityPostBase):
    pass


class CommunityPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    post_type: Optional[PostType] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    script_id: Optional[int] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_spoiler: Optional[bool] = None


class CommunityPost(CommunityPostBase):
    id: int
    author_id: Optional[int] = None
    username: Optional[str] = None
    author_name: Optional[str] = None
    avatar: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    comments: List[Comment] = []

    class Config:
        from_attributes = True
