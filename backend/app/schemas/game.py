from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field
from ..models import GameStatus, AssignmentMethod


class CharacterAssignment(BaseModel):
    user_id: int
    character_name: str
    is_approved: bool = False


class GameParticipant(BaseModel):
    user_id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    joined_at: datetime
    character_assignment: Optional[CharacterAssignment] = None

    class Config:
        from_attributes = True


class GameBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    script_id: int
    game_date: date
    start_time: time
    location: Optional[str] = None
    max_players: int = Field(..., ge=2)
    notes: Optional[str] = None
    assignment_method: AssignmentMethod = AssignmentMethod.MANUAL
    price_per_person: Optional[float] = None


class GameCreate(GameBase):
    dm_id: Optional[int] = None


class GameUpdate(BaseModel):
    title: Optional[str] = None
    game_date: Optional[date] = None
    start_time: Optional[time] = None
    location: Optional[str] = None
    max_players: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[GameStatus] = None
    assignment_method: Optional[AssignmentMethod] = None
    price_per_person: Optional[float] = None


class Game(GameBase):
    id: int
    creator_id: int
    dm_id: Optional[int] = None
    status: GameStatus = GameStatus.RECRUITING
    current_players: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    participants: List[GameParticipant] = []

    class Config:
        from_attributes = True


class GameList(BaseModel):
    id: int
    title: str
    script_id: int
    script_title: Optional[str] = None
    game_date: date
    start_time: time
    location: Optional[str] = None
    max_players: int
    current_players: int
    status: GameStatus
    creator_id: int
    creator_name: Optional[str] = None
    dm_id: Optional[int] = None
    dm_name: Optional[str] = None
    created_at: datetime
    price_per_person: Optional[float] = None

    class Config:
        from_attributes = True
