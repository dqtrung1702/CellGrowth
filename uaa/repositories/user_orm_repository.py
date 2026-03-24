from datetime import datetime
from typing import Optional

from sqlalchemy import select

from models.entities import User
from models.orm import get_session
from .interfaces import UserRepoProtocol


class UserOrmRepository(UserRepoProtocol):
    """ORM-backed implementation for core auth flows (login/register)."""

    def __init__(self, session_factory=get_session):
        self._session_factory = session_factory

    def get_by_username(self, username: str):
        with self._session_factory() as session:
            stmt = select(User).where(User.username == username).limit(1)
            user = session.execute(stmt).scalar_one_or_none()
            if not user:
                return None
            return {
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "userlocked": user.userlocked,
            }

    def insert_user(self, username: str, password_hash, name_display: str):
        with self._session_factory() as session:
            user = User(
                username=username,
                password=password_hash,
                userlocked=False,
                name_display=name_display,
                last_signon_datetime=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user.id

    def update_last_signon(self, user_id: int):
        with self._session_factory() as session:
            user: Optional[User] = session.get(User, user_id)
            if not user:
                return
            user.last_signon_datetime = datetime.utcnow()
            session.commit()

    # --- methods below are unused by AuthService but required by protocol ---
    def get_username(self, user_id: int):
        raise NotImplementedError

    def list_users(self, *args, **kwargs):
        raise NotImplementedError

    def get_user_info(self, *args, **kwargs):
        raise NotImplementedError

    def update_user_fields(self, *args, **kwargs):
        raise NotImplementedError

    def replace_user_roles(self, *args, **kwargs):
        raise NotImplementedError

    def get_roles_of_user(self, *args, **kwargs):
        raise NotImplementedError

    def list_users_by_role(self, *args, **kwargs):
        raise NotImplementedError

    def add_roles(self, *args, **kwargs):
        raise NotImplementedError

    def set_data_permission(self, *args, **kwargs):
        raise NotImplementedError
