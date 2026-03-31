from datetime import datetime
from typing import List, Iterable, Optional

from sqlalchemy import text
from sqlalchemy import func

from .orm_base import OrmRepo
from .set_repository import SetRepository
from models.orm import SessionLocal
from models.entities import (
    Permission,
    UrlPermission,
    PagePermission,
    DataPermission,
)


class PermissionRepository(OrmRepo):
    def __init__(self, session_factory=None):
        sf = session_factory or SessionLocal
        super().__init__(sf)
        self.set_repo = SetRepository(sf)

    # Listing helpers -------------------------------------------------
    def list_permissions_orm(self, filters: List, limit: int, offset: int):
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
                    Permission.last_update_username.label("LastUpdateUserName"),
                    Permission.last_update_datetime.label("LastUpdateDateTime"),
                )
                .order_by(Permission.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total, [dict(r._mapping) for r in rows]

    def list_public_data_permissions_orm(self, filters: List, limit: int, offset: int):
        with self.session() as session:
            base = session.query(Permission).filter(Permission.permission_type == "DATA")
            for f in filters:
                base = base.filter(f)
            total = base.with_entities(func.count()).scalar() or 0
            rows = (
                base.with_entities(
                    Permission.id,
                    Permission.code.label("Code"),
                    Permission.description.label("Description"),
                )
                .order_by(Permission.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return total, [dict(r._mapping) for r in rows]

    def list_dataset_by_permission(self, pid: int):
        """ORM-based lấy dataset theo permission, hạn chế text()."""
        from models.entities import DataPermission, Set, Dataset, Permission
        with self.session() as session:
            q = (
                session.query(
                    Set.id.label("SetId"),
                    Set.setname.label("SetName"),
                    Set.services.label("Services"),
                    Set.setcode.label("SetCode"),
                    Dataset.tablename.label("Table"),
                    Dataset.colname.label("Column"),
                    Dataset.colval.label("Value"),
                )
                .join(DataPermission, DataPermission.set_id == Set.id)
                .join(Permission, Permission.id == DataPermission.permission_id)
                .outerjoin(Dataset, Dataset.set_id == Set.id)
                .filter(DataPermission.permission_id == pid, Permission.permission_type == "DATA")
                .order_by(Set.id, Dataset.id)
            )
            return [dict(r._mapping) for r in q.all()]

    def list_url_by_permission(self, pid: int):
        """ORM-based trả URL + page theo permission."""
        from sqlalchemy import literal, func
        from models.entities import UrlPermission, PagePermission
        with self.session() as session:
            url_q = (
                session.query(
                    UrlPermission.id,
                    UrlPermission.url,
                    UrlPermission.method.label("Method"),
                    UrlPermission.type.label("Type"),
                )
                .filter(UrlPermission.permission_id == pid)
                .filter(func.upper(UrlPermission.type) != "PAGE")
            )
            page_q = session.query(
                PagePermission.id,
                PagePermission.page.label("url"),
                literal("GET").label("Method"),
                literal("PAGE").label("Type"),
            ).filter(PagePermission.permission_id == pid)
            rows = url_q.union_all(page_q).all()
            return [dict(r._mapping) for r in rows]

    def list_urls_by_permissions(self, perm_ids: List[int], perm_codes: List[str]):
        """ORM-based URLs theo danh sách permission id/code."""
        from sqlalchemy import literal, func, or_
        from models.entities import UrlPermission, PagePermission, Permission
        with self.session() as session:
            conds = []
            if perm_ids:
                conds.append(Permission.id.in_(perm_ids))
            if perm_codes:
                conds.append(Permission.code.in_(perm_codes))
            if not conds:
                return []

            base_filter = or_(*conds)

            url_q = (
                session.query(
                    UrlPermission.url,
                    UrlPermission.method.label("Method"),
                    UrlPermission.type.label("Type"),
                )
                .join(Permission, Permission.id == UrlPermission.permission_id)
                .filter(func.upper(UrlPermission.type) != "PAGE")
                .filter(base_filter)
            )
            page_q = (
                session.query(
                    PagePermission.page.label("url"),
                    literal("GET").label("Method"),
                    literal("PAGE").label("Type"),
                )
                .join(Permission, Permission.id == PagePermission.permission_id)
                .filter(base_filter)
            )
            rows = url_q.union_all(page_q).all()
            return [dict(r._mapping) for r in rows]

    def list_pages_by_user(self, user_id: int):
        """ORM-based: tìm page_permissions qua user_roles -> role_permissions."""
        from models.entities import UserRole, RolePermission, PagePermission
        with self.session() as session:
            q = (
                session.query(
                    PagePermission.page.label("Page"),
                    PagePermission.permission_id.label("PermissionId"),
                )
                .join(RolePermission, RolePermission.permission_id == PagePermission.permission_id)
                .join(UserRole, UserRole.role_id == RolePermission.role_id)
                .filter(UserRole.user_id == user_id)
                .distinct()
            )
            return [dict(r._mapping) for r in q.all()]

    def list_data_set_by_user(self, user_id: int):
        """ORM-based dataset theo user qua roles -> data_permissions."""
        from models.entities import UserRole, RolePermission, Permission, DataPermission, Set, Dataset
        with self.session() as session:
            q = (
                session.query(
                    Set.id.label("SetId"),
                    Set.setname.label("SetName"),
                    Set.services.label("Services"),
                    Set.setcode.label("SetCode"),
                    Dataset.tablename.label("Table"),
                    Dataset.colname.label("Column"),
                    Dataset.colval.label("Value"),
                )
                .select_from(UserRole)
                .join(RolePermission, RolePermission.role_id == UserRole.role_id)
                .join(Permission, Permission.id == RolePermission.permission_id)
                .join(DataPermission, DataPermission.permission_id == Permission.id)
                .join(Set, Set.id == DataPermission.set_id)
                .outerjoin(Dataset, Dataset.set_id == Set.id)
                .filter(UserRole.user_id == user_id, Permission.permission_type == "DATA")
                .distinct()
            )
            return [dict(r._mapping) for r in q.all()]

    def get_permission_info(self, ids: List[int], extra_condition: str, params: List):
        with self.session() as session:
            sql, bind = self._bind_sql(
                f"""
                SELECT id AS "id", code AS "Code", code AS "PermissionName",
                       permission_type AS "PermissionType",
                       description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM permissions
                WHERE id = ANY(%s) {extra_condition};
                """,
                [ids] + params,
            )
            rows = session.execute(text(sql), bind).mappings().all()

            set_rows = session.execute(
                text(
                    """
                    SELECT DISTINCT dp.permission_id,
                                    s.id AS set_id,
                                    s.setname,
                                    s.services,
                                    s.setcode
                    FROM data_permissions dp
                    JOIN sets s ON s.id = dp.set_id
                    WHERE dp.permission_id = ANY(:ids);
                    """
                ),
                {"ids": ids},
            ).mappings().all()

            data_by_set = {}
            if set_rows:
                set_ids = [r["set_id"] for r in set_rows]
                ds_rows = session.execute(
                    text(
                        """
                        SELECT set_id, tablename, colname, colval
                        FROM datasets
                        WHERE set_id = ANY(:set_ids);
                        """
                    ),
                    {"set_ids": set_ids},
                ).mappings().all()
                for r in ds_rows:
                    data_by_set.setdefault(r["set_id"], []).append(
                        {"Table": r["tablename"], "Column": r["colname"], "Value": r["colval"]}
                    )

                by_pid = {}
                for r in set_rows:
                    pid = r["permission_id"]
                    set_id = r["set_id"]
                    ds_entry = {
                        "SetId": set_id,
                        "SetName": r["setname"],
                        "Services": r["services"],
                        "SetCode": r["setcode"],
                    }
                    if set_id in data_by_set:
                        ds_entry["Data"] = data_by_set[set_id]
                    by_pid.setdefault(pid, []).append(ds_entry)

                for row in rows:
                    pid = row["id"]
                    row["DataSets"] = by_pid.get(pid, [])
            return rows

    # Insert/update/delete --------------------------------------------
    def get_permission_type(self, pid: int):
        with self.session() as session:
            return session.execute(
                text("SELECT permission_type FROM permissions WHERE id=:pid;"),
                {"pid": pid},
            ).scalar_one_or_none()

    def insert_permission(self, code: str, ptype: str, description: Optional[str], url_list: Iterable, data_sets: Iterable):
        with self.session() as session:
            perm = Permission(
                code=code,
                permission_type=ptype,
                description=description,
                last_update_username="system",
                last_update_datetime=datetime.utcnow(),
            )
            session.add(perm)
            session.flush()
            pid = perm.id

            if ptype == "DATA":
                for ds in data_sets:
                    set_id = self.set_repo.resolve_set_id(session, ds if isinstance(ds, dict) else {})
                    session.add(
                        DataPermission(
                            permission_id=pid,
                            set_id=set_id,
                            last_update_datetime=datetime.utcnow(),
                        )
                    )
            else:
                self._insert_url_or_page(session, pid, url_list)
            return pid

    def update_permission(self, pid: int, description, ptype: str, url_list: List, data_sets: List[dict]):
        with self.session() as session:
            perm = session.get(Permission, pid)
            if not perm:
                raise ValueError("Permission not found")
            if description is not None:
                perm.description = description
            if ptype is not None:
                perm.permission_type = ptype
            perm.last_update_datetime = datetime.utcnow()

            # Capture current scopes to preserve when client sends empty lists
            existing_urls = self.list_url_by_permission(pid) if perm.permission_type != "DATA" else []
            existing_sets = []
            if perm.permission_type == "DATA":
                existing_sets = self.list_dataset_by_permission(pid)

            session.query(UrlPermission).filter(UrlPermission.permission_id == pid).delete(synchronize_session=False)
            session.query(PagePermission).filter(PagePermission.permission_id == pid).delete(synchronize_session=False)
            session.query(DataPermission).filter(DataPermission.permission_id == pid).delete(synchronize_session=False)

            if perm.permission_type == "DATA":
                # If client didn't send datasets, keep old ones
                target_sets = data_sets or existing_sets
                for ds in target_sets:
                    set_id = self.set_repo.resolve_set_id(session, ds if isinstance(ds, dict) else {})
                    session.add(
                        DataPermission(
                            permission_id=pid,
                            set_id=set_id,
                            last_update_datetime=datetime.utcnow(),
                        )
                    )
            else:
                target_urls = url_list or existing_urls
                self._insert_url_or_page(session, pid, target_urls)

    def delete_permission(self, pid: int):
        with self.session() as session:
            session.query(UrlPermission).filter(UrlPermission.permission_id == pid).delete(synchronize_session=False)
            session.query(PagePermission).filter(PagePermission.permission_id == pid).delete(synchronize_session=False)
            session.query(DataPermission).filter(DataPermission.permission_id == pid).delete(synchronize_session=False)
            session.query(Permission).filter(Permission.id == pid).delete(synchronize_session=False)

    # Helpers ---------------------------------------------------------
    def _insert_url_or_page(self, session, pid: int, url_list: Iterable):
        for entry in url_list:
            is_page = False
            if isinstance(entry, dict):
                type_val_raw = (entry.get("Type") or entry.get("type") or "").upper()
                page_val = entry.get("page") or entry.get("Page") or ""
                is_page = type_val_raw == "PAGE" or bool(page_val)
            else:
                page_val = ""
                type_val_raw = ""
            if is_page:
                if isinstance(entry, dict):
                    page_val = page_val or entry.get("url") or entry.get("Url") or ""
                else:
                    page_val = str(entry)
                if not page_val:
                    continue
                session.add(
                    PagePermission(
                        permission_id=pid,
                        page=page_val,
                        last_update_datetime=datetime.utcnow(),
                    )
                )
            else:
                if isinstance(entry, dict):
                    url_val = entry.get("url") or entry.get("Url") or ""
                    method_val = (entry.get("Method") or entry.get("method") or "GET").upper()
                    type_val = type_val_raw or "ROLE"
                else:
                    url_val = str(entry)
                    method_val = "GET"
                    type_val = "ROLE"
                if not url_val:
                    continue
                session.add(
                    UrlPermission(
                        permission_id=pid,
                        url=url_val,
                        method=method_val,
                        type=type_val,
                        last_update_datetime=datetime.utcnow(),
                    )
                )
