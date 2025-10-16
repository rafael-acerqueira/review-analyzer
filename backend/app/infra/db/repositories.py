from typing import Optional
from sqlmodel import Session, select

from app.models.user import User as UserModel
from app.domain.auth.entities import UserEntity
from app.domain.auth.interfaces import UserRepository


class SqlModelUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, row: Optional[UserModel]) -> Optional[UserEntity]:
        if not row:
            return None
        return UserEntity(
            id=row.id,
            email=row.email,
            role=getattr(row, "role", None),
            hashed_password=getattr(row, "hashed_password", None),
            provider=getattr(row, "provider", None),
            sub=getattr(row, "sub", None),
        )

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        row = self.db.exec(select(UserModel).where(UserModel.email == email)).first()
        return self._to_entity(row)

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        row = self.db.get(UserModel, user_id)
        return self._to_entity(row)

    def exists_email(self, email: str) -> bool:
        row = self.db.exec(select(UserModel).where(UserModel.email == email)).first()
        return row is not None

    def create_local(self, *, email: str, hashed_password: str) -> UserEntity:
        user = UserModel(email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._to_entity(user)

    def upsert_google_user(self, *, email: str, sub: str) -> UserEntity:
        user = self.db.exec(select(UserModel).where(UserModel.email == email)).first()
        if not user:
            user = UserModel(email=email, provider="google", sub=sub)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return self._to_entity(user)

        updated = False
        if getattr(user, "sub", None) != sub:
            user.sub = sub
            updated = True
        if not getattr(user, "provider", None):
            user.provider = "google"
            updated = True
        if updated:
            self.db.commit()
            self.db.refresh(user)
        return self._to_entity(user)

    def update_google_sub_if_needed(self, *, user_id: int, sub: str) -> Optional[UserEntity]:
        user = self.db.get(UserModel, user_id)
        if not user:
            return None
        if getattr(user, "sub", None) != sub:
            user.sub = sub
            if not getattr(user, "provider", None):
                user.provider = "google"
            self.db.commit()
            self.db.refresh(user)
        return self._to_entity(user)
