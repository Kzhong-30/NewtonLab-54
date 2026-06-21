from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from .base import CRUDBase
from ..models import Script, Character, DifficultyLevel, ScriptType
from ..schemas import ScriptCreate, ScriptUpdate


class CRUDScript(CRUDBase[Script, ScriptCreate, ScriptUpdate]):
    def create(self, db: Session, *, obj_in: ScriptCreate, store_id: int) -> Script:
        obj_in_data = obj_in.model_dump(exclude={"characters"})
        db_obj = Script(**obj_in_data, store_id=store_id)
        db.add(db_obj)
        db.flush()
        for char_data in obj_in.characters:
            char_obj = Character(**char_data.model_dump(), script_id=db_obj.id)
            db.add(char_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_type(self, db: Session, script_type: ScriptType, skip: int = 0, limit: int = 100) -> List[Script]:
        return db.query(Script).filter(Script.script_type == script_type).offset(skip).limit(limit).all()

    def get_by_difficulty(self, db: Session, difficulty: DifficultyLevel, skip: int = 0, limit: int = 100) -> List[Script]:
        return db.query(Script).filter(Script.difficulty == difficulty).offset(skip).limit(limit).all()

    def get_by_players(self, db: Session, min_players: int, max_players: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Script]:
        query = db.query(Script).filter(Script.min_players <= min_players)
        if max_players:
            query = query.filter(Script.max_players >= max_players)
        else:
            query = query.filter(Script.max_players >= min_players)
        return query.offset(skip).limit(limit).all()

    def get_filtered(
        self,
        db: Session,
        script_type: Optional[ScriptType] = None,
        difficulty: Optional[DifficultyLevel] = None,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        store_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Script]:
        query = db.query(Script)
        if script_type:
            query = query.filter(Script.script_type == script_type)
        if difficulty:
            query = query.filter(Script.difficulty == difficulty)
        if min_players:
            query = query.filter(Script.min_players <= min_players)
        if max_players:
            query = query.filter(Script.max_players >= max_players)
        if store_id:
            query = query.filter(Script.store_id == store_id)
        if is_approved is not None:
            query = query.filter(Script.is_approved == is_approved)
        return query.offset(skip).limit(limit).all()

    def get_count_filtered(
        self,
        db: Session,
        script_type: Optional[ScriptType] = None,
        difficulty: Optional[DifficultyLevel] = None,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        store_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
    ) -> int:
        query = db.query(func.count(Script.id))
        if script_type:
            query = query.filter(Script.script_type == script_type)
        if difficulty:
            query = query.filter(Script.difficulty == difficulty)
        if min_players:
            query = query.filter(Script.min_players <= min_players)
        if max_players:
            query = query.filter(Script.max_players >= max_players)
        if store_id:
            query = query.filter(Script.store_id == store_id)
        if is_approved is not None:
            query = query.filter(Script.is_approved == is_approved)
        return query.scalar()


script = CRUDScript(Script)
