import json
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import text

from repositories.access_request_repository import AccessRequestRepository
from repositories.user_repository import UserRepository
from repositories.interfaces import AccessRequestRepoProtocol, UserRepoProtocol
from services.access_request_apply_service import AccessRequestApplyService
from queries.access_request_query import AccessRequestQuery, AccessRequestFilter
from utils.data_scope import data_scope_filters
from models.orm import SessionLocal
from schemas.response import PaginationMeta, ResponseEnvelope


class AccessRequestService:
    def __init__(self, ar_repo: Optional[AccessRequestRepoProtocol] = None, user_repo: Optional[UserRepoProtocol] = None, apply_service: Optional[AccessRequestApplyService] = None, query: Optional[AccessRequestQuery] = None):
        self.ar_repo: AccessRequestRepoProtocol = ar_repo or AccessRequestRepository()
        self.user_repo: UserRepoProtocol = user_repo or UserRepository()
        self.apply_service = apply_service or AccessRequestApplyService()
        self.query = query or AccessRequestQuery(SessionLocal)

    # ---------- helpers ----------
    def _apply_items(self, items: List[dict], target_user: int) -> List[dict]:
        return self.apply_service.apply_items(items, target_user, self.user_repo)

    # ---------- commands ----------
    def create(self, requester_id: int, username: str, req_type: str, reason: str, ttl_hours: Optional[int], roles: List[int], data_perms: List[int]):
        req_id = self.ar_repo.create_request(requester_id, username, req_type, reason, ttl_hours)
        items = []
        items.extend([{"role_id": rid} for rid in roles])
        items.extend([{"data_permission_id": dp} for dp in data_perms])
        self.ar_repo.add_items(req_id, items)
        self.ar_repo.log_action(req_id, requester_id, "SUBMIT", note=reason)
        return req_id

    def list(self, user_id: int, payload) -> ResponseEnvelope:
        scope_sql, scope_params = data_scope_filters(SessionLocal, user_id, table_name="access_requests", alias="access_requests", deny_if_no_user=True)

        created_from_dt = None
        created_to_dt = None
        if getattr(payload, "created_from", None):
            try:
                created_from_dt = datetime.fromisoformat(payload.created_from)
            except Exception:
                created_from_dt = None
        if getattr(payload, "created_to", None):
            try:
                created_to_dt = datetime.fromisoformat(payload.created_to)
                if created_to_dt and created_to_dt.time().hour == 0 and created_to_dt.time().minute == 0:
                    created_to_dt = created_to_dt + timedelta(days=1)
            except Exception:
                created_to_dt = None

        flt = AccessRequestFilter(
            status=getattr(payload, "status", None),
            request_type=getattr(payload, "type", None),
            requester=getattr(payload, "requester", None),
            created_from=created_from_dt,
            created_to=created_to_dt,
            scope_sql=scope_sql,
            scope_params=scope_params or [],
        )
        offset = (payload.page - 1) * payload.page_size
        total, rows = self.query.list_requests(flt, payload.page_size, offset)
        meta = PaginationMeta(page=payload.page, page_size=payload.page_size, total=total)
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def get(self, req_id: int):
        return self.ar_repo.get_request_with_items(req_id)

    def update(self, req_id: int, requester_id: int, roles: Optional[List[int]], data_perms: Optional[List[int]], reason: Optional[str]):
        req_row, items, _ = self.ar_repo.get_request_with_items(req_id)
        if not req_row:
            return None
        if req_row.get("requester_id") != requester_id:
            return "FORBIDDEN"
        if req_row.get("status") != "SUBMITTED":
            return req_row

        # Update reason
        self.ar_repo.reject_request  # noop keep reference for style
        with self.ar_repo.session() as session:
            session.execute(
                text(
                    """
                    UPDATE access_requests
                    SET reason = COALESCE(:reason, reason), updated_at = :ts
                    WHERE id = :rid;
                    """
                ),
                {"reason": reason, "ts": datetime.utcnow(), "rid": req_id},
            )

        # Replace items if provided
        if roles is not None or data_perms is not None:
            new_items = []
            if roles:
                new_items.extend([{"role_id": rid} for rid in roles])
            if data_perms:
                new_items.extend([{"data_permission_id": dp} for dp in data_perms])
            if new_items:
                self.ar_repo.replace_items(req_id, new_items)

        self.ar_repo.log_action(req_id, requester_id, "UPDATE", note=reason)
        return req_row
