from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole, GameStatus, AssignmentMethod, Game, GameParticipant, CharacterAssignment
from ..schemas import Game, GameCreate, GameUpdate, GameList, GameParticipant, CharacterAssignment
from ..crud import game as crud_game
from ..core.security import get_current_user

router = APIRouter(prefix="/games", tags=["组局"])


@router.get("/", response_model=List[GameList])
def get_games(
    *,
    db: Session = Depends(get_db),
    status: Optional[GameStatus] = Query(None, description="游戏状态"),
    script_id: Optional[int] = Query(None, description="剧本ID"),
    store_id: Optional[int] = Query(None, description="店家ID"),
    dm_id: Optional[int] = Query(None, description="DM ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    query = db.query(Game)
    if status:
        query = query.filter(Game.status == status)
    if script_id:
        query = query.filter(Game.script_id == script_id)
    if store_id:
        query = query.filter(Game.store_id == store_id)
    if dm_id:
        query = query.filter(Game.dm_id == dm_id)
    games = query.order_by(Game.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for g in games:
        game_dict = {
            "id": g.id,
            "title": g.title,
            "script_id": g.script_id,
            "script_title": g.script.title if g.script else None,
            "scheduled_time": datetime.combine(g.game_date, g.start_time) if g.game_date and g.start_time else None,
            "location": g.location,
            "max_players": g.max_players,
            "current_players": g.current_players,
            "status": g.status,
            "creator_id": g.creator_id,
            "creator_name": g.creator.nickname or g.creator.username if g.creator else None,
            "dm_id": g.dm_id,
            "dm_name": g.dm.user.nickname or g.dm.user.username if g.dm and g.dm.user else None,
            "is_private": False,
            "price_per_person": g.price_per_person
        }
        result.append(game_dict)
    return result


@router.get("/my", response_model=List[GameList])
def get_my_games(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[GameStatus] = Query(None, description="游戏状态"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    games = crud_game.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    if status:
        games = [g for g in games if g.status == status]
    result = []
    for g in games:
        game_dict = {
            "id": g.id,
            "title": g.title,
            "script_id": g.script_id,
            "script_title": g.script.title if g.script else None,
            "scheduled_time": datetime.combine(g.game_date, g.start_time) if g.game_date and g.start_time else None,
            "location": g.location,
            "max_players": g.max_players,
            "current_players": g.current_players,
            "status": g.status,
            "creator_id": g.creator_id,
            "creator_name": g.creator.nickname or g.creator.username if g.creator else None,
            "dm_id": g.dm_id,
            "dm_name": g.dm.user.nickname or g.dm.user.username if g.dm and g.dm.user else None,
            "is_private": False,
            "price_per_person": g.price_per_person
        }
        result.append(game_dict)
    return result


@router.get("/{game_id}", response_model=Game)
def get_game(
    *,
    db: Session = Depends(get_db),
    game_id: int
) -> Any:
    game = crud_game.get(db, id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="游戏不存在"
        )
    participants = []
    for p in game.participants:
        assignment = None
        for a in game.character_assignments:
            if a.user_id == p.user_id:
                assignment = {
                    "user_id": a.user_id,
                    "character_name": a.character.name if a.character else "",
                    "is_approved": True
                }
                break
        participants.append({
            "user_id": p.user_id,
            "username": p.user.username,
            "nickname": p.user.nickname,
            "avatar": p.user.avatar,
            "joined_at": p.joined_at,
            "character_assignment": assignment
        })
    return {
        "id": game.id,
        "title": game.title,
        "script_id": game.script_id,
        "scheduled_time": datetime.combine(game.game_date, game.start_time) if game.game_date and game.start_time else None,
        "location": game.location,
        "max_players": game.max_players,
        "description": game.notes,
        "notes": game.notes,
        "is_private": False,
        "assignment_method": game.assignment_method,
        "price_per_person": game.price_per_person,
        "creator_id": game.creator_id,
        "dm_id": game.dm_id,
        "status": game.status,
        "current_players": game.current_players,
        "created_at": game.created_at,
        "updated_at": game.updated_at,
        "participants": participants
    }


@router.post("/", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    game_in: GameCreate
) -> Any:
    game_data = game_in.model_dump()
    scheduled_time = game_data.pop("scheduled_time")
    db_game = Game(
        title=game_data["title"],
        script_id=game_data["script_id"],
        store_id=current_user.store_profile.id if current_user.store_profile else None,
        dm_id=game_data.get("dm_id"),
        creator_id=current_user.id,
        game_date=scheduled_time.date(),
        start_time=scheduled_time.time(),
        max_players=game_data["max_players"],
        status=GameStatus.RECRUITING,
        assignment_method=game_data.get("assignment_method", AssignmentMethod.MANUAL),
        price_per_person=game_data.get("price_per_person", 0.0),
        location=game_data.get("location"),
        notes=game_data.get("notes")
    )
    db.add(db_game)
    db.flush()
    participant = GameParticipant(game_id=db_game.id, user_id=current_user.id, notes="游戏创建者")
    db.add(participant)
    db_game.current_players = 1
    db.commit()
    db.refresh(db_game)
    return get_game(db=db, game_id=db_game.id)