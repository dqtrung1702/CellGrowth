from typing import List, Optional

from repositories.user_repository import UserRepository
from repositories.interfaces import UserRepoProtocol
from utils.data_scope import data_scope_filters
from models.orm import SessionLocal
from schemas.response import ResponseEnvelope, PaginationMeta
from utils.query_builder import QueryBuilder
from models.entities import User


class UserService:
    def __init__(self, user_repo: Optional[UserRepoProtocol] = None):
        self.user_repo: UserRepoProtocol = user_repo or UserRepository()

    def list_users(self, requester_id: Optional[int], page: int, page_size: int, username_filter: Optional[str]):
        scope_sql, scope_params = data_scope_filters(
            SessionLocal,
            requester_id,
            table_name="users",
            service_name="uaa",
            alias="users",
            deny_if_no_user=False,
        )

        qb = QueryBuilder(model=User)
        qb.add_ilike("username", username_filter).add_raw(scope_sql, scope_params or [])
        filters = qb.filters()

        total_row, rows = self.user_repo.list_users(filters, page_size, (page - 1) * page_size)
        meta = PaginationMeta(page=page, page_size=page_size, total=total_row, total_row=[{"sum": total_row}])
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def get_user_info(self, requester_id: Optional[int], user_id: int):
        scope_sql, scope_params = data_scope_filters(
            SessionLocal,
            requester_id,
            table_name="users",
            service_name="uaa",
            alias="u",
            deny_if_no_user=False,
        )
        qb = QueryBuilder(model=User)
        qb.add_equals("id", user_id)
        qb.add_raw(scope_sql, scope_params or [])
        row = self.user_repo.get_user_info(qb.filters())
        if not row:
            return ResponseEnvelope(status="FAIL", message="User not found")
        row["DataPermission"] = row.get("DataPermissionCode") or ""
        return ResponseEnvelope(status="OK", data=[row])

    def update_user(self, user_id: int, user_locked, password: Optional[str], name_display: Optional[str], data_permission):
        fields = {}
        if user_locked is not None:
            fields["userlocked"] = bool(user_locked)

        if password:
            try:
                import bcrypt

                hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            except Exception:
                hashed = password.encode("utf-8")
            fields["password"] = hashed

        if name_display is not None:
            fields["name_display"] = name_display

        if data_permission is not None:
            dp = data_permission
            if isinstance(dp, (list, tuple)):
                dp = dp[0] if dp else None
            if dp in ("", None, 0, "0"):
                dp = None
            try:
                dp = int(dp) if dp is not None else None
            except Exception:
                dp = None
            fields["data_permission_id"] = dp

        if not fields:
            return ResponseEnvelope(status="FAIL", message="No fields to update")

        self.user_repo.update_user_fields(user_id, fields)
        return ResponseEnvelope(status="OK")

    def update_user_role(self, user_id: int, role_ids: List[int]):
        self.user_repo.replace_user_roles(user_id, [int(r) for r in role_ids])
        return ResponseEnvelope(status="OK")
