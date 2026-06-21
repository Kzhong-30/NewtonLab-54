from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole, Review
from ..schemas import Review as ReviewSchema, ReviewCreate, ReviewUpdate
from ..crud import review as crud_review
from ..core.security import get_current_user

router = APIRouter(prefix="/reviews", tags=["评价"])


@router.get("/", response_model=List[ReviewSchema])
def get_reviews(
    *,
    db: Session = Depends(get_db),
    script_id: Optional[int] = None,
    game_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    reviews = crud_review.get_filtered(
        db,
        script_id=script_id,
        game_id=game_id,
        skip=skip,
        limit=limit
    )
    result = []
    for r in reviews:
        result.append({
            "id": r.id,
            "script_id": r.script_id,
            "rating": float(r.rating),
            "content": r.content,
            "is_spoiler": False,
            "author_id": r.author_id,
            "game_id": r.game_id,
            "username": r.author.username if r.author else None,
            "avatar": r.author.avatar if r.author else None,
            "likes_count": 0,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        })
    return result


@router.get("/{review_id}", response_model=ReviewSchema)
def get_review(
    *,
    db: Session = Depends(get_db),
    review_id: int
) -> ReviewSchema:
    review = crud_review.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    return {
        "id": review.id,
        "script_id": review.script_id,
        "rating": float(review.rating),
        "content": review.content,
        "is_spoiler": False,
        "author_id": review.author_id,
        "game_id": review.game_id,
        "username": review.author.username if review.author else None,
        "avatar": review.author.avatar if review.author else None,
        "likes_count": 0,
        "created_at": review.created_at,
        "updated_at": review.updated_at
    }


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
def create_review(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    review_in: ReviewCreate
) -> Any:
    review = crud_review.create(db, obj_in=review_in, author_id=current_user.id)
    return {
        "id": review.id,
        "script_id": review.script_id,
        "rating": float(review.rating),
        "content": review.content,
        "is_spoiler": False,
        "author_id": review.author_id,
        "game_id": review.game_id,
        "username": review.author.username if review.author else None,
        "avatar": review.author.avatar if review.author else None,
        "likes_count": 0,
        "created_at": review.created_at,
        "updated_at": review.updated_at
    }


@router.put("/{review_id}", response_model=ReviewSchema)
def update_review(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    review_id: int,
    review_in: ReviewUpdate
) -> ReviewSchema:
    review = crud_review.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    if review.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此评价"
        )
    review = crud_review.update(db, db_obj=review, obj_in=review_in)
    return {
        "id": review.id,
        "script_id": review.script_id,
        "rating": float(review.rating),
        "content": review.content,
        "is_spoiler": False,
        "author_id": review.author_id,
        "game_id": review.game_id,
        "username": review.author.username if review.author else None,
        "avatar": review.author.avatar if review.author else None,
        "likes_count": 0,
        "created_at": review.created_at,
        "updated_at": review.updated_at
    }


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    review_id: int
) -> None:
    review = crud_review.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    if review.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此评价"
        )
    crud_review.remove(db, id=review_id)
