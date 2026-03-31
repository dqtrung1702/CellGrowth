from datetime import datetime
from typing import List

from sqlalchemy import text, func

from .orm_base import OrmRepo
from models.entities import Role, Permission, RolePermission, UserRole


class RoleRepository(OrmRepo):
    def list_roles_orm(self, filters: List, limit: int, offset: int):
        with self.session() as session:
            count_q = session.query(func.count()).select_from(Role)
            base = session.query(Role)
            for f in filters:
                count_q = count_q.filter(f)
                base = base.filter(f)
            total = count_q.scalar() or 0
            rows = (
                base.with_entities(
                    Role.id,
                    Role.code.label("Code"),
                    Role.description.label("Description"),
                    Role.last_update_username.label("LastUpdateUserName"),
                    Role.last_update_datetime.label("LastUpdateDateTime"),
                )
                .order_by(Role.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total, [dict(r._mapping) for r in rows]

    def list_public_roles_orm(self, filters: List, limit: int, offset: int):
        with self.session() as session:
            count_q = session.query(func.count()).select_from(Role)
            base = session.query(Role)
            for f in filters:
                count_q = count_q.filter(f)
                base = base.filter(f)
            total = count_q.scalar() or 0
            rows = (
                base.with_entities(Role.id, Role.code.label("Code"), Role.description.label("Description"))
                .order_by(Role.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total, [dict(r._mapping) for r in rows]

    def get_role(self, role_id, extra_condition: str, params: List):
        with self.session() as session:
            sql, bind = self._bind_sql("id = %s " + extra_condition if extra_condition else "id = %s", [role_id] + params)
            row = (
                session.query(
                    Role.id,
                    Role.code.label("Code"),
                    Role.description.label("Description"),
                    Role.last_update_username.label("LastUpdateUserName"),
                    Role.last_update_datetime.label("LastUpdateDateTime"),
                )
                .filter(text(sql)).params(**bind)
                .first()
            )
            return dict(row._mapping) if row else None

    def insert_role(self, code: str, description: str, permissions: List[int]):
        with self.session() as session:
            role = Role(code=code, description=description, last_update_username="system", last_update_datetime=datetime.utcnow())
            session.add(role)
            session.flush()
            for pid in permissions:
                session.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=pid,
                        last_update_datetime=datetime.utcnow(),
                    )
                )
            return role.id

    def update_role(self, role_id, description, permissions: List[int]):
        with self.session() as session:
            role = session.get(Role, role_id)
            if not role:
                return
            if description is not None:
                role.description = description
            role.last_update_datetime = datetime.utcnow()
            session.query(RolePermission).filter(RolePermission.role_id == role_id).delete(synchronize_session=False)
            for pid in permissions:
                session.add(
                    RolePermission(
                        role_id=role_id,
                        permission_id=pid,
                        last_update_datetime=datetime.utcnow(),
                    )
                )

    def delete_role(self, role_id):
        with self.session() as session:
            session.query(RolePermission).filter(RolePermission.role_id == role_id).delete(synchronize_session=False)
            session.query(UserRole).filter(UserRole.role_id == role_id).delete(synchronize_session=False)
            session.query(Role).filter(Role.id == role_id).delete(synchronize_session=False)

    def list_permissions_of_role(self, role_id):
        with self.session() as session:
            rows = (
                session.query(
                    Permission.id.label("PermissionId"),
                    Permission.code.label("PermissionName"),
                )
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .filter(RolePermission.role_id == role_id)
                .all()
            )
            return [dict(r._mapping) for r in rows]

    def list_roles_of_permission(self, permission_id):
        with self.session() as session:
            rows = (
                session.query(
                    Role.id.label("RoleId"),
                    Role.code.label("RoleName"),
                )
                .join(RolePermission, RolePermission.role_id == Role.id)
                .filter(RolePermission.permission_id == permission_id)
                .all()
            )
            return [dict(r._mapping) for r in rows]

    def list_role_permissions(self, filters: List, limit: int, offset: int):
        with self.session() as session:
            base = session.query(Permission)
            for f in filters:
                base = base.filter(f)
            total = base.with_entities(func.count()).scalar() or 0
            rows = (
                base.with_entities(
                    Permission.id,
                    Permission.code.label("Code"),
                    Permission.permission_type.label("PermissionType"),
                    Permission.description.label("Description"),
                )
                .order_by(Permission.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total, [dict(r._mapping) for r in rows]
