from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserRole, Review
from ..schemas import Review, ReviewCreate, ReviewUpdate
from ..crud import review as crud_review
from ..core.security import get_current_user

router = APIRouter(prefix="/reviews", tags=["评价"])


@router.get("/", response_model=List[Review])
def get_reviews(
    *,
    db: Session = Depends(get_db),
    script_id: Optional[int] = None,
    game_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    return crud_review.get_multi(db, skip=skip, limit=limit)


@router.get("/{review_id}", response_model=Review)
def get_review(
    *,
    db: Session = Depends(get_db),
    review_id: int
) -> None:
    review = crud_review.get(db, id=review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评价不存在"
        )
    return review


@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    review_in: ReviewCreate
) -> Any:
    return crud_review.create(db, obj_in=review_in)


@router.put("/{review_id}", response_model=Review)
def update_review(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    review_id: int,
    review_in: ReviewUpdate
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
            detail="没有权限修改此评价"
        )
    return crud_review.update(db, db_obj=review, obj_in=review_in)


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
