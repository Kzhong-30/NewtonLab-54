import random
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .base import CRUDBase
from ..models import Game, GameParticipant, CharacterAssignment, GameStatus, Script, Character
from ..schemas import GameCreate, GameUpdate


class CRUDGame(CRUDBase[Game, GameCreate, GameUpdate]):
    def create(self, db: Session, *, obj_in: GameCreate, creator_id: int) -> Game:
        obj_in_data = obj_in.model_dump()
        db_obj = Game(**obj_in_data, creator_id=creator_id)
        db.add(db_obj)
        db.flush()
        participant = GameParticipant(game_id=db_obj.id, user_id=creator_id, notes="游戏创建者")
        db.add(participant)
        db_obj.current_players = 1
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def join_game(self, db: Session, *, game_id: int, user_id: int) -> Optional[Game]:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        if game.status not in [GameStatus.RECRUITING, GameStatus.FULL]:
            return None
        if game.current_players >= game.max_players:
            return None
        existing = db.query(GameParticipant).filter(
            and_(GameParticipant.game_id == game_id, GameParticipant.user_id == user_id)
        ).first()
        if existing:
            return game
        participant = GameParticipant(game_id=game_id, user_id=user_id)
        db.add(participant)
        game.current_players += 1
        if game.current_players >= game.max_players:
            game.status = GameStatus.FULL
        db.commit()
        db.refresh(game)
        return game

    def leave_game(self, db: Session, *, game_id: int, user_id: int) -> Optional[Game]:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        if game.status in [GameStatus.IN_PROGRESS, GameStatus.COMPLETED]:
            return None
        if game.creator_id == user_id:
            return None
        participant = db.query(GameParticipant).filter(
            and_(GameParticipant.game_id == game_id, GameParticipant.user_id == user_id)
        ).first()
        if not participant:
            return game
        db.delete(participant)
        game.current_players -= 1
        if game.status == GameStatus.FULL and game.current_players < game.max_players:
            game.status = GameStatus.RECRUITING
        assignments = db.query(CharacterAssignment).filter(
            and_(CharacterAssignment.game_id == game_id, CharacterAssignment.user_id == user_id)
        ).all()
        for assignment in assignments:
            db.delete(assignment)
        db.commit()
        db.refresh(game)
        return game

    def assign_characters_random(self, db: Session, *, game_id: int, assigned_by: int) -> Optional[Game]:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        db.query(CharacterAssignment).filter(CharacterAssignment.game_id == game_id).delete()
        script = db.query(Script).filter(Script.id == game.script_id).first()
        if not script:
            return None
        participants = db.query(GameParticipant).filter(GameParticipant.game_id == game_id).all()
        characters = db.query(Character).filter(Character.script_id == script.id).all()
        user_ids = [p.user_id for p in participants]
        char_ids = [c.id for c in characters]
        min_count = min(len(user_ids), len(char_ids))
        random.shuffle(char_ids)
        for i in range(min_count):
            assignment = CharacterAssignment(
                game_id=game_id,
                user_id=user_ids[i],
                character_id=char_ids[i],
                assigned_by=assigned_by
            )
            db.add(assignment)
        db.commit()
        db.refresh(game)
        return game

    def assign_character_manual(
        self,
        db: Session,
        *,
        game_id: int,
        user_id: int,
        character_id: int,
        assigned_by: int
    ) -> Optional[CharacterAssignment]:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        participant = db.query(GameParticipant).filter(
            and_(GameParticipant.game_id == game_id, GameParticipant.user_id == user_id)
        ).first()
        if not participant:
            return None
        character = db.query(Character).filter(
            and_(Character.id == character_id, Character.script_id == game.script_id)
        ).first()
        if not character:
            return None
        existing = db.query(CharacterAssignment).filter(
            and_(CharacterAssignment.game_id == game_id, CharacterAssignment.user_id == user_id)
        ).first()
        if existing:
            db.delete(existing)
        existing_char = db.query(CharacterAssignment).filter(
            and_(CharacterAssignment.game_id == game_id, CharacterAssignment.character_id == character_id)
        ).first()
        if existing_char:
            db.delete(existing_char)
        assignment = CharacterAssignment(
            game_id=game_id,
            user_id=user_id,
            character_id=character_id,
            assigned_by=assigned_by
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    def start_game(self, db: Session, *, game_id: int) -> Optional[Game]:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        if game.status not in [GameStatus.RECRUITING, GameStatus.FULL]:
            return None
        game.status = GameStatus.IN_PROGRESS
        db.commit()
        db.refresh(game)
        return game

    def complete_game(self, db: Session, *, game_id: int) -> Optional[Game]:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        if game.status != GameStatus.IN_PROGRESS:
            return None
        game.status = GameStatus.COMPLETED
        db.commit()
        db.refresh(game)
        return game

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Game]:
        return db.query(Game).join(GameParticipant).filter(
            GameParticipant.user_id == user_id
        ).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: GameStatus, skip: int = 0, limit: int = 100) -> List[Game]:
        return db.query(Game).filter(Game.status == status).offset(skip).limit(limit).all()


game = CRUDGame(Game)
