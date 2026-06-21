from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from ..models import DifficultyLevel


class Character(BaseModel):
    name: str
    gender: Optional[str] = None
    age: Optional[str] = None
    description: Optional[str] = None
    background: Optional[str] = None
    secrets: Optional[str] = None
    relationships: Optional[dict] = None


class ScriptBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    cover_image: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    duration: Optional[int] = None
    player_count_min: int = Field(..., ge=2)
    player_count_max: int = Field(..., ge=2)
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    synopsis: Optional[str] = None
    background_story: Optional[str] = None
    characters: Optional[List[Character]] = None
    is_public: bool = True


class ScriptCreate(ScriptBase):
    pass


class ScriptUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    duration: Optional[int] = None
    player_count_min: Optional[int] = None
    player_count_max: Optional[int] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    synopsis: Optional[str] = None
    background_story: Optional[str] = None
    characters: Optional[List[Character]] = None
    is_public: Optional[bool] = None


class Script(ScriptBase):
    id: int
    author_id: int
    rating: Optional[float] = None
    review_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScriptList(BaseModel):
    id: int
    title: str
    cover_image: Optional[str] = None
    difficulty: DifficultyLevel
    duration: Optional[int] = None
    player_count_min: int
    player_count_max: int
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: int = 0
    author_name: Optional[str] = None

    class Config:
        from_attributes = True
