from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole, Script, DifficultyLevel, ScriptType
from ..schemas import Script, ScriptCreate, ScriptUpdate, ScriptList
from ..crud import script as crud_script
from ..core.security import get_current_user

router = APIRouter(prefix="/scripts", tags=["剧本"])


@router.get("/", response_model=List[ScriptList])
def get_scripts(
    *,
    db: Session = Depends(get_db),
    script_type: Optional[ScriptType] = Query(None, description="剧本类型"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="难度"),
    min_players: Optional[int] = Query(None, ge=2, description="最少人数"),
    max_players: Optional[int] = Query(None, ge=2, description="最多人数"),
    is_approved: Optional[bool] = Query(True, description="是否审核通过"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> Any:
    scripts = crud_script.get_filtered(
        db,
        script_type=script_type,
        difficulty=difficulty,
        min_players=min_players,
        max_players=max_players,
        is_approved=is_approved,
        skip=skip,
        limit=limit
    )
    result = []
    for s in scripts:
        result.append({
            "id": s.id,
            "title": s.title,
            "cover_image": s.cover_image,
            "difficulty": s.difficulty,
            "duration": s.estimated_duration,
            "player_count_min": s.min_players,
            "player_count_max": s.max_players,
            "genre": s.script_type.value if s.script_type else None,
            "tags": [],
            "rating": s.average_rating,
            "review_count": s.total_reviews,
            "author_name": s.store.store_name if s.store else None
        })
    return result


@router.get("/{script_id}", response_model=Script)
def get_script(
    *,
    db: Session = Depends(get_db),
    script_id: int
) -> Any:
    script = crud_script.get(db, id=script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )
    characters = []
    for c in script.characters:
        characters.append({
            "name": c.name,
            "gender": c.gender.value if c.gender else None,
            "age": str(c.age) if c.age else None,
            "description": c.description,
            "background": c.background_story,
            "secrets": None,
            "relationships": None
        })
    return {
        "id": script.id,
        "title": script.title,
        "description": script.description,
        "cover_image": script.cover_image,
        "difficulty": script.difficulty,
        "duration": script.estimated_duration,
        "player_count_min": script.min_players,
        "player_count_max": script.max_players,
        "genre": script.script_type.value if script.script_type else None,
        "tags": [],
        "synopsis": script.description,
        "background_story": None,
        "characters": characters,
        "is_public": script.is_approved,
        "author_id": script.store_id,
        "rating": script.average_rating,
        "review_count": script.total_reviews,
        "created_at": script.created_at,
        "updated_at": script.updated_at
    }


@router.post("/", response_model=Script, status_code=status.HTTP_201_CREATED)
def create_script(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    script_in: ScriptCreate
) -> Any:
    if current_user.role not in [UserRole.STORE_OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有店家或管理员才能创建剧本"
        )
    store_profile = current_user.store_profile
    if not store_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先完善店家资料"
        )
    script = crud_script.create(db, obj_in=script_in, store_id=store_profile.id)
    return get_script(db=db, script_id=script.id)


@router.put("/{script_id}", response_model=Script)
def update_script(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    script_id: int,
    script_in: ScriptUpdate
) -> Any:
    script = crud_script.get(db, id=script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )
    if current_user.role != UserRole.ADMIN and script.store_id != current_user.store_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此剧本"
        )
    script = crud_script.update(db, db_obj=script, obj_in=script_in)
    return get_script(db=db, script_id=script.id)


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_script(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    script_id: int
) -> None:
    script = crud_script.get(db, id=script_id)
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="剧本不存在"
        )
    if current_user.role != UserRole.ADMIN and script.store_id != current_user.store_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此剧本"
        )
    crud_script.remove(db, id=script_id)
    return None
