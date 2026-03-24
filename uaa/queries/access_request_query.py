from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple, Callable

from sqlalchemy import text, func
from sqlalchemy.orm import Session

from models.entities import AccessRequest

SessionFactory = Callable[[], Session]


@dataclass
class AccessRequestFilter:
    status: Optional[str] = None
    request_type: Optional[str] = None
    requester: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    scope_sql: Optional[str] = None
    scope_params: Optional[List] = None


class AccessRequestQuery:
    """Query object bọc ORM để tránh rò rỉ SQL vào controller/service."""

    def __init__(self, session_factory: SessionFactory):
        self.session_factory = session_factory

    def _apply_filters(self, query, flt: AccessRequestFilter):
        if flt.status:
            query = query.filter(AccessRequest.status == flt.status.upper())
        if flt.request_type:
            query = query.filter(AccessRequest.request_type == flt.request_type.upper())
        if flt.requester:
            query = query.filter(AccessRequest.requester.ilike(f"%{flt.requester}%"))
        if flt.created_from:
            query = query.filter(AccessRequest.created_at >= flt.created_from)
        if flt.created_to:
            query = query.filter(AccessRequest.created_at < flt.created_to)
        if flt.scope_sql:
            sql, bind = self._bind_sql(flt.scope_sql, flt.scope_params or [])
            query = query.filter(text(sql)).params(**bind)
        return query

    @staticmethod
    def _bind_sql(sql: str, params: List):
        """
        Chuyển %s -> :p0,:p1 để dùng với sqlalchemy.text.
        """
        if not params:
            return sql, {}
        bound = {}
        parts = sql.split("%s")
        rebuilt = []
        for i, part in enumerate(parts):
            rebuilt.append(part)
            if i < len(parts) - 1:
                key = f"p{i}"
                rebuilt.append(f":{key}")
                bound[key] = params[i]
        return "".join(rebuilt), bound

    @staticmethod
    def _to_dict(row: AccessRequest):
        return {
            "id": row.id,
            "requester_id": row.requester_id,
            "requester_username": row.requester,
            "request_type": row.request_type,
            "status": row.status,
            "reason": row.reason,
            "ttl_hours": row.ttl_hours,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "approved_by": row.approved_by,
            "approved_at": row.approved_at,
        }

    def list_requests(self, flt: AccessRequestFilter, limit: int, offset: int) -> Tuple[int, List[dict]]:
        with self.session_factory() as session:
            base_q = session.query(AccessRequest)
            base_q = self._apply_filters(base_q, flt)
            total = base_q.with_entities(func.count()).scalar()
            rows = (
                base_q.order_by(AccessRequest.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total or 0, [self._to_dict(r) for r in rows]
