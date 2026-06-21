from typing import Any, List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole, DMProfile, DMSchedule, GameStatus
from ..schemas import DMProfile, DMProfileCreate, DMProfileUpdate, DMSchedule, DMScheduleCreate
from ..crud import dm as crud_dm
from ..core.security import get_current_user

router = APIRouter(prefix="/dm", tags=["DM管理"])


@router.get("/", response_model=List[DMProfile])
def get_dms(
    *,
    db: Session = Depends(get_db),
    is_certified: Optional[bool] = Query(None, description="是否认证"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    if is_certified:
        dms = crud_dm.get_certified_dms(db, skip=skip, limit=limit)
    else:
        dms = crud_dm.get_multi(db, skip=skip, limit=limit)
    result = []
    for dm in dms:
        result.append({
            "id": dm.id,
            "user_id": dm.user_id,
            "real_name": dm.real_name,
            "avatar": dm.user.avatar if dm.user else None,
            "bio": dm.description,
            "experience_years": dm.experience_years,
            "specialty_genres": dm.good_script_types if dm.good_script_types else [],
            "scripts_mastered": [],
            "hourly_rate": 0.0,
            "rating": dm.average_rating,
            "review_count": dm.total_games,
            "total_games_hosted": dm.total_games,
            "is_verified": dm.is_approved,
            "certification": None,
            "username": dm.user.nickname or dm.user.username if dm.user else None,
            "schedules": [],
            "created_at": dm.created_at,
            "updated_at": dm.updated_at
        })
    return result


@router.get("/me", response_model=DMProfile)
def get_my_dm_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if current_user.role not in [UserRole.DM, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有DM或管理员才能访问"
        )
    dm = crud_dm.get_by_user_id(db, user_id=current_user.id)
    if not dm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DM资料不存在，请先提交认证"
        )
    schedules = []
    for s in dm.schedules:
        schedules.append({
            "id": s.id,
            "schedule_date": s.date,
            "start_time": s.start_time.strftime("%H:%M") if s.start_time else "00:00",
            "end_time": s.end_time.strftime("%H:%M") if s.end_time else "00:00",
            "is_available": s.is_available,
            "notes": None,
            "dm_id": s.dm_id,
            "created_at": s.created_at
        })
    return {
        "id": dm.id,
        "user_id": dm.user_id,
        "real_name": dm.real_name,
        "avatar": dm.user.avatar if dm.user else None,
        "bio": dm.description,
        "experience_years": dm.experience_years,
        "specialty_genres": dm.good_script_types if dm.good_script_types else [],
        "scripts_mastered": [],
        "hourly_rate": 0.0,
        "rating": dm.average_rating,
        "review_count": dm.total_games,
        "total_games_hosted": dm.total_games,
        "is_verified": dm.is_approved,
        "certification": None,
        "username": dm.user.nickname or dm.user.username if dm.user else None,
        "schedules": schedules,
        "created_at": dm.created_at,
        "updated_at": dm.updated_at
    }


@router.post("/profile", response_model=DMProfile, status_code=status.HTTP_201_CREATED)
def create_dm_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_in: DMProfileCreate
) -> Any:
    existing = crud_dm.get_by_user_id(db, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DM资料已存在"
        )
    profile_data = profile_in.model_dump()
    db_profile = DMProfile(
        user_id=current_user.id,
        real_name=profile_data.get("real_name"),
        id_card=profile_data.get("certification"),
        experience_years=profile_data.get("experience_years", 0),
        description=profile_data.get("bio"),
        good_script_types=profile_data.get("specialty_genres"),
        is_approved=False
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return get_dm_profile(db=db, dm_id=db_profile.id)


@router.put("/profile", response_model=DMProfile)
def update_dm_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    profile_in: DMProfileUpdate
) -> Any:
    dm = crud_dm.get_by_user_id(db, user_id=current_user.id)
    if not dm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DM资料不存在，请先创建"
        )
    if dm.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此资料"
        )
    update_data = profile_in.model_dump(exclude_unset=True)
    if "bio" in update_data:
        update_data["description"] = update_data.pop("bio")
    if "specialty_genres" in update_data:
        update_data["good_script_types"] = update_data.pop("specialty_genres")
    if "certification" in update_data:
        update_data["id_card"] = update_data.pop("certification")
    for field, value in update_data.items():
        if value is not None and hasattr(dm, field):
            setattr(dm, field, value)
    db.add(dm)
    db.commit()
    db.refresh(dm)
    return get_dm_profile(db=db, dm_id=dm.id)
@router.get("/{dm_id}", response_model=DMProfile)
def get_dm_profile(
    *,
    db: Session = Depends(get_db),
    dm_id: int
) -> Any:
    dm = crud_dm.get(db, id=dm_id)
    if not dm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DM不存在"
        )
    schedules = []
    for s in dm.schedules:
        schedules.append({
            "id": s.id,
            "schedule_date": s.date,
            "start_time": s.start_time.strftime("%H:%M") if s.start_time else "00:00",
            "end_time": s.end_time.strftime("%H:%M") if s.end_time else "00:00",
            "is_available": s.is_available,
            "notes": None,
            "dm_id": s.dm_id,
            "created_at": s.created_at
        })
    return {
        "id": dm.id,
        "user_id": dm.user_id,
        "real_name": dm.real_name,
        "avatar": dm.user.avatar if dm.user else None,
        "bio": dm.description,
        "experience_years": dm.experience_years,
        "specialty_genres": dm.good_script_types if dm.good_script_types else [],
        "scripts_mastered": [],
        "hourly_rate": 0.0,
        "rating": dm.average_rating,
        "review_count": dm.total_games,
        "total_games_hosted": dm.total_games,
        "is_verified": dm.is_approved,
        "certification": None,
        "username": dm.user.nickname or dm.user.username if dm.user else None,
        "schedules": schedules,
        "created_at": dm.created_at,
        "updated_at": dm.updated_at
    }


