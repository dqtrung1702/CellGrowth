from datetime import datetime
from typing import List, Optional

from sqlalchemy import text, func

from .orm_base import OrmRepo
from models.entities import User, Permission, Role, UserRole


class UserRepository(OrmRepo):
    def get_by_username(self, username: str):
        with self.session() as session:
            row = (
                session.query(User.id, User.username, User.password, User.userlocked)
                .filter(User.username == username)
                .first()
            )
            return dict(row._mapping) if row else None

    def get_by_id(self, user_id: int):
        with self.session() as session:
            row = (
                session.query(User.id, User.username, User.userlocked)
                .filter(User.id == user_id)
                .first()
            )
            return dict(row._mapping) if row else None

    def insert_user(self, username: str, password_hash, name_display: str):
        with self.session() as session:
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
            session.flush()
            return user.id

    def get_username(self, user_id: int):
        with self.session() as session:
            row = session.query(User.username).filter(User.id == user_id).first()
            return row[0] if row else None

    def update_last_signon(self, user_id: int):
        with self.session() as session:
            session.query(User).filter(User.id == user_id).update(
                {"last_signon_datetime": datetime.utcnow()}, synchronize_session=False
            )

    def list_users(self, filters: List, limit: int, offset: int):
        with self.session() as session:
            base = session.query(User)
            for f in filters:
                base = base.filter(f)
            total = base.with_entities(func.count()).scalar() or 0
            rows = (
                base.with_entities(
                    User.id,
                    User.username.label("UserName"),
                    User.last_signon_datetime.label("LastSignOnDateTime"),
                    User.updated_at.label("LastUpdateDateTime"),
                )
                .order_by(User.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total, [dict(r._mapping) for r in rows]

    def get_user_info(self, filters: List):
        with self.session() as session:
            base = (
                session.query(
                    User.id,
                    User.username.label("UserName"),
                    User.userlocked.label("UserLocked"),
                    User.last_signon_datetime.label("LastSignOnDateTime"),
                    User.updated_at.label("LastUpdateDateTime"),
                    User.username.label("LastUpdateUserName"),
                    User.name_display.label("NameDisplay"),
                    User.data_permission_id.label("DataPermissionId"),
                    Permission.code.label("DataPermissionCode"),
                )
                .outerjoin(Permission, Permission.id == User.data_permission_id)
            )
            for f in filters:
                base = base.filter(f)
            row = base.first()
            return dict(row._mapping) if row else None

    def update_user_fields(self, user_id: int, fields: dict):
        if not fields:
            return
        fields["updated_at"] = datetime.utcnow()
        with self.session() as session:
            session.query(User).filter(User.id == user_id).update(fields, synchronize_session=False)

    def replace_user_roles(self, user_id: int, role_ids: List[int]):
        with self.session() as session:
            session.query(UserRole).filter(UserRole.user_id == user_id).delete(synchronize_session=False)
            for rid in role_ids:
                session.add(
                    UserRole(
                        user_id=user_id,
                        role_id=rid,
                        last_update_datetime=datetime.utcnow(),
                    )
                )

    def get_roles_of_user(self, user_id: int):
        with self.session() as session:
            rows = (
                session.query(Role.id.label("RoleId"), Role.code.label("Role"))
                .join(UserRole, UserRole.role_id == Role.id)
                .filter(UserRole.user_id == user_id)
                .all()
            )
            return [dict(r._mapping) for r in rows]

    def list_users_by_role(self, role_id: int):
        with self.session() as session:
            rows = (
                session.query(User.username.label("UserName"))
                .join(UserRole, UserRole.user_id == User.id)
                .filter(UserRole.role_id == role_id)
                .all()
            )
            return [dict(r._mapping) for r in rows]

    def add_roles(self, user_id: int, role_ids: List[int]):
        with self.session() as session:
            for rid in role_ids:
                session.add(
                    UserRole(
                        user_id=user_id,
                        role_id=rid,
                        last_update_datetime=datetime.utcnow(),
                    )
                )

    def set_data_permission(self, user_id: int, permission_id: Optional[int]):
        with self.session() as session:
            session.query(User).filter(User.id == user_id).update(
                {"data_permission_id": permission_id, "updated_at": datetime.utcnow()}, synchronize_session=False
            )
