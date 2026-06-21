from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class DMScheduleBase(BaseModel):
    schedule_date: date
    start_time: str
    end_time: str
    is_available: bool = True
    notes: Optional[str] = None


class DMScheduleCreate(DMScheduleBase):
    pass


class DMScheduleUpdate(BaseModel):
    schedule_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = None


class DMSchedule(DMScheduleBase):
    id: int
    dm_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DMProfileBase(BaseModel):
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    specialty_genres: Optional[List[str]] = None
    scripts_mastered: Optional[List[int]] = None
    hourly_rate: Optional[float] = None
    rating: Optional[float] = None
    review_count: int = 0
    total_games_hosted: int = 0
    is_verified: bool = False
    certification: Optional[str] = None


class DMProfileCreate(DMProfileBase):
    user_id: int


class DMProfileUpdate(BaseModel):
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    specialty_genres: Optional[List[str]] = None
    scripts_mastered: Optional[List[int]] = None
    hourly_rate: Optional[float] = None
    certification: Optional[str] = None


class DMProfile(DMProfileBase):
    id: int
    user_id: int
    username: Optional[str] = None
    schedules: List[DMSchedule] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
