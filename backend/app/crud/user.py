from typing import Optional
from sqlalchemy.orm import Session
from .base import CRUDBase
from ..models import User
from ..schemas import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password



class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def authenticate(self, db: Session, *, username_or_email: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username_or_email)
        if not user:
            user = self.get_by_email(db, email=username_or_email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user



user = CRUDUser(User)
