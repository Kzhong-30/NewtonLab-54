from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from .base import CRUDBase
from ..models import DMProfile, DMSchedule, DMIncomeRecord, Game, GameStatus
from ..schemas import DMProfileCreate, DMProfileUpdate, DMScheduleCreate, DMScheduleUpdate


class CRUDDM(CRUDBase[DMProfile, DMProfileCreate, DMProfileUpdate]):
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[DMProfile]:
        return db.query(DMProfile).filter(DMProfile.user_id == user_id).first()

    def get_certified_dms(self, db: Session, skip: int = 0, limit: int = 100) -> List[DMProfile]:
        return db.query(DMProfile).filter(DMProfile.is_approved == True).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: DMProfileCreate, user_id: int) -> DMProfile:
        obj_in_data = obj_in.model_dump()
        db_obj = DMProfile(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_income_stats(
        self,
        db: Session,
        dm_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[int, float]:
        query = db.query(
            func.count(DMIncomeRecord.id),
            func.sum(DMIncomeRecord.amount)
        ).filter(DMIncomeRecord.dm_id == dm_id)
        if start_date:
            query = query.filter(DMIncomeRecord.settled_at >= start_date)
        if end_date:
            query = query.filter(DMIncomeRecord.settled_at <= end_date)
        total_games, total_income = query.first()
        return total_games or 0, total_income or 0.0

    def add_income_record(
        self,
        db: Session,
        *,
        dm_id: int,
        game_id: int,
        amount: float,
        notes: Optional[str] = None
    ) -> DMIncomeRecord:
        record = DMIncomeRecord(
            dm_id=dm_id,
            game_id=game_id,
            amount=amount,
            notes=notes
        )
        db.add(record)
        dm_profile = db.query(DMProfile).filter(DMProfile.id == dm_id).first()
        if dm_profile:
            dm_profile.total_income += amount
            dm_profile.total_games += 1
        db.commit()
        db.refresh(record)
        return record

    def add_schedule(self, db: Session, *, dm_id: int, obj_in: DMScheduleCreate) -> DMSchedule:
        obj_in_data = obj_in.model_dump()
        db_obj = DMSchedule(**obj_in_data, dm_id=dm_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_schedules(
        self,
        db: Session,
        dm_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_available: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DMSchedule]:
        query = db.query(DMSchedule).filter(DMSchedule.dm_id == dm_id)
        if start_date:
            query = query.filter(DMSchedule.date >= start_date.date())
        if end_date:
            query = query.filter(DMSchedule.date <= end_date.date())
        if is_available is not None:
            query = query.filter(DMSchedule.is_available == is_available)
        return query.offset(skip).limit(limit).all()

    def update_schedule(self, db: Session, *, schedule_id: int, obj_in: DMScheduleUpdate) -> Optional[DMSchedule]:
        schedule = db.query(DMSchedule).filter(DMSchedule.id == schedule_id).first()
        if not schedule:
            return None
        return super().update(db, db_obj=schedule, obj_in=obj_in)

    def delete_schedule(self, db: Session, *, schedule_id: int) -> Optional[DMSchedule]:
        schedule = db.query(DMSchedule).filter(DMSchedule.id == schedule_id).first()
        if not schedule:
            return None
        db.delete(schedule)
        db.commit()
        return schedule

    def get_available_dms(
        self,
        db: Session,
        date: datetime,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[DMProfile]:
        target_date = date.date()
        target_start = start_time.time()
        target_end = end_time.time()
        subquery = db.query(DMSchedule.dm_id).filter(
            and_(
                DMSchedule.date == target_date,
                DMSchedule.start_time < target_end,
                DMSchedule.end_time > target_start,
                DMSchedule.is_available == False
            )
        ).subquery()
        return db.query(DMProfile).filter(
            and_(
                DMProfile.is_approved == True,
                DMProfile.id.notin_(subquery)
            )
        ).offset(skip).limit(limit).all()

    def get_games_hosted(
        self,
        db: Session,
        dm_id: int,
        status: Optional[GameStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Game]:
        query = db.query(Game).filter(Game.dm_id == dm_id)
        if status:
            query = query.filter(Game.status == status)
        return query.offset(skip).limit(limit).all()


dm = CRUDDM(DMProfile)
