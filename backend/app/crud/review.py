from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from .base import CRUDBase
from ..models import Review, Game, Script
from ..schemas import ReviewCreate, ReviewUpdate


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    def create(self, db: Session, *, obj_in: ReviewCreate, author_id: int) -> Review:
        obj_in_data = obj_in.model_dump()
        db_obj = Review(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_game(self, db: Session, game_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(Review.game_id == game_id).offset(skip).limit(limit).all()

    def get_by_script(self, db: Session, script_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(Review.script_id == script_id).offset(skip).limit(limit).all()

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(Review.author_id == user_id).offset(skip).limit(limit).all()

    def get_by_target_user(self, db: Session, target_user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).filter(Review.target_user_id == target_user_id).offset(skip).limit(limit).all()

    def get_by_store(self, db: Session, store_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return db.query(Review).join(Game).join(Script).filter(
            Script.store_id == store_id
        ).offset(skip).limit(limit).all()

    def get_filtered(
        self,
        db: Session,
        game_id: Optional[int] = None,
        script_id: Optional[int] = None,
        user_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        store_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        query = db.query(Review)
        if game_id:
            query = query.filter(Review.game_id == game_id)
        if script_id:
            query = query.filter(Review.script_id == script_id)
        if user_id:
            query = query.filter(Review.author_id == user_id)
        if target_user_id:
            query = query.filter(Review.target_user_id == target_user_id)
        if store_id:
            query = query.join(Game).join(Script).filter(Script.store_id == store_id)
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        if max_rating:
            query = query.filter(Review.rating <= max_rating)
        return query.offset(skip).limit(limit).all()

    def get_average_rating_by_script(self, db: Session, script_id: int) -> float:
        result = db.query(func.avg(Review.rating)).filter(Review.script_id == script_id).scalar()
        return float(result) if result else 0.0

    def get_average_rating_by_user(self, db: Session, target_user_id: int) -> float:
        result = db.query(func.avg(Review.rating)).filter(Review.target_user_id == target_user_id).scalar()
        return float(result) if result else 0.0


review = CRUDReview(Review)
