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
    def _fmt_dt(val):
        if hasattr(val, "strftime"):
            offset = val.strftime("%z") or "+0000"
            millis = int(getattr(val, "microsecond", 0) / 1000)
            return f"{val.strftime('%Y-%m-%dT%H:%M:%S')}.{millis:03d}{offset}"
        return val

    @classmethod
    def _to_dict(cls, row: AccessRequest):
        return {
            "id": row.id,
            "requester_id": row.requester_id,
            "requester_username": row.requester,
            "request_type": row.request_type,
            "status": row.status,
            "reason": row.reason,
            "ttl_hours": row.ttl_hours,
            "created_at": cls._fmt_dt(row.created_at),
            "updated_at": cls._fmt_dt(row.updated_at),
            "approved_by": row.approved_by,
            "approved_at": cls._fmt_dt(row.approved_at),
        }

    def list_requests(self, flt: AccessRequestFilter, limit: int, offset: int) -> Tuple[int, List[dict]]:
        with self.session_factory() as session:
            # Count with explicit FROM to avoid losing table when using with_entities
            count_q = session.query(func.count()).select_from(AccessRequest)
            count_q = self._apply_filters(count_q, flt)
            total = count_q.scalar()

            base_q = session.query(AccessRequest)
            base_q = self._apply_filters(base_q, flt)
            rows = (
                base_q.order_by(AccessRequest.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total or 0, [self._to_dict(r) for r in rows]
