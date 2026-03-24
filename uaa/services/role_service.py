from typing import List, Optional

from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from repositories.interfaces import RoleRepoProtocol, UserRepoProtocol
from utils.data_scope import data_scope_filters
from models.orm import SessionLocal
from utils.query_builder import QueryBuilder
from schemas.response import ResponseEnvelope, PaginationMeta
from models.entities import Role, Permission


class RoleService:
    def __init__(self, role_repo: Optional[RoleRepoProtocol] = None, user_repo: Optional[UserRepoProtocol] = None):
        self.role_repo: RoleRepoProtocol = role_repo or RoleRepository()
        self.user_repo: UserRepoProtocol = user_repo or UserRepository()

    def list_roles(self, requester_id: Optional[int], page: int, page_size: int, code: Optional[str]):
        scope_sql, scope_params = data_scope_filters(SessionLocal, requester_id, table_name="roles")
        qb = QueryBuilder(model=Role)
        qb.add_ilike("code", code).add_raw(scope_sql, scope_params or [])
        filters = qb.filters()
        total, rows = self.role_repo.list_roles_orm(filters, page_size, (page - 1) * page_size)
        meta = PaginationMeta(page=page, page_size=page_size, total=total, total_row=[{"sum": total}])
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def public_roles(self, page: int, page_size: int, code: Optional[str]):
        qb = QueryBuilder(model=Role)
        qb.add_ilike("code", code)
        filters = qb.filters()
        total, rows = self.role_repo.list_public_roles_orm(filters, page_size, (page - 1) * page_size)
        meta = PaginationMeta(page=page, page_size=page_size, total=total)
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def get_role_info(self, requester_id: Optional[int], role_id: int):
        scope_sql, scope_params = data_scope_filters(SessionLocal, requester_id, table_name="roles")
        extra = (" AND " + scope_sql) if scope_sql else ""
        row = self.role_repo.get_role(role_id, extra, scope_params or [])
        if not row:
            return ResponseEnvelope(status="FAIL", message="Role not found")
        return ResponseEnvelope(status="OK", data=[row])

    def add_role(self, code: str, description: Optional[str], perm_ids: List[int]):
        rid = self.role_repo.insert_role(code, description, perm_ids)
        return ResponseEnvelope(status="OK", data={"id": rid})

    def update_role(self, rid: int, description: Optional[str], perm_ids: List[int]):
        self.role_repo.update_role(rid, description, perm_ids)
        return ResponseEnvelope(status="OK")

    def delete_role(self, rid: int):
        self.role_repo.delete_role(rid)
        return ResponseEnvelope(status="OK")

    def permissions_of_role(self, rid: int):
        rows = self.role_repo.list_permissions_of_role(rid)
        return ResponseEnvelope(status="OK", data=rows)

    def users_of_role(self, rid: int):
        rows = self.user_repo.list_users_by_role(rid)
        return ResponseEnvelope(status="OK", data=rows)

    def roles_of_user(self, uid: int):
        rows = self.user_repo.get_roles_of_user(uid)
        return ResponseEnvelope(status="OK", data=rows)

    def role_permission_list(self, page: int, page_size: int, code: Optional[str], ptype):
        offset = (page - 1) * page_size
        qb = QueryBuilder(model=Permission)
        if ptype:
            if isinstance(ptype, (list, tuple, set)):
                qb.add_any("permission_type", list(ptype))
            else:
                qb.add_equals("permission_type", ptype)
        else:
            qb.add_any("permission_type", ["ROLE", "PAGE"])
        if code:
            qb.add_ilike("code", code)
        filters = qb.filters()
        total, rows = self.role_repo.list_role_permissions(filters, page_size, offset)
        meta = PaginationMeta(page=page, page_size=page_size, total=total, total_row=[{"sum": total}])
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def roles_by_permission(self, pid: int):
        rows = self.role_repo.list_roles_of_permission(pid)
        return ResponseEnvelope(status="OK", data=rows)
