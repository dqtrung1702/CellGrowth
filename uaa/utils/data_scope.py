import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable

from sqlalchemy import select
from sqlalchemy.orm import Session
from models.entities import User, DataPermission, Permission, Set, Dataset


SessionFactory = Callable[[], Session]


@dataclass
class ScopeResult:
    where: Optional[str]
    params: List

    @property
    def full_access(self) -> bool:
        return self.where is None and self.params is None

    @property
    def deny_all(self) -> bool:
        return self.where == "1=0"

    def __iter__(self):
        yield self.where
        yield self.params

    def apply(self, target_list):
        if self.where:
            target_list.append(self.where)
        return target_list


def data_scope_filters(session_factory: SessionFactory, user_id: Optional[int], table_name: str, service_name: str = "uaa", alias: Optional[str] = None, deny_if_no_user: bool = True) -> ScopeResult:
    """
    Build SQL WHERE fragment enforcing data scopes for a user.
    Returns ScopeResult(where_sql, params). If where is None, caller can treat as full access.
    """
    if not user_id:
        return ScopeResult("1=0", []) if deny_if_no_user else ScopeResult(None, None)

    with session_factory() as session:
        perm_id = session.execute(select(User.data_permission_id).where(User.id == user_id)).scalar_one_or_none()
        if not perm_id:
            return ScopeResult("1=0", []) if deny_if_no_user else ScopeResult(None, None)

        stmt = (
            select(
                Set.services.label("Services"),
                Dataset.tablename.label("Table"),
                Dataset.colname.label("Column"),
                Dataset.colval.label("Value"),
            )
            .select_from(DataPermission)
            .join(Permission, Permission.id == DataPermission.permission_id)
            .join(Set, Set.id == DataPermission.set_id)
            .join(Dataset, Dataset.set_id == Set.id, isouter=True)
            .where(DataPermission.permission_id == perm_id, Permission.permission_type == "DATA")
        )
        scopes = session.execute(stmt).mappings().all()

    scopes = [sc for sc in scopes if sc.get("Table")]
    if not scopes:
        return ScopeResult("1=0", []) if deny_if_no_user else ScopeResult(None, None)

    service_name = (service_name or "").lower()
    table_name = (table_name or "").lower()

    filters: List[Tuple[str, str]] = []
    wildcard = False
    for sc in scopes:
        svc = (sc.get("Services") or "*").lower()
        tbl = (sc.get("Table") or "*").lower()
        col = sc.get("Column") or "*"
        val = sc.get("Value") or "*"

        if svc not in ("*", service_name):
            continue
        if tbl not in ("*", table_name):
            continue
        if col == "*" or val == "*":
            wildcard = True
            continue
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", col):
            continue
        filters.append((col, val))

    if wildcard and not filters:
        return ScopeResult(None, None)
    if not filters:
        return ScopeResult("1=0", []) if deny_if_no_user else ScopeResult(None, None)

    clauses = []
    params = []
    prefix = f"{alias}." if alias else ""
    for col, val in filters:
        clauses.append(f"{prefix}{col} = %s")
        params.append(val)

    return ScopeResult("(" + " OR ".join(clauses) + ")", params)
