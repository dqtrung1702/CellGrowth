from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from repositories.permission_repository import PermissionRepository
from repositories.interfaces import PermissionRepoProtocol
from utils.data_scope import data_scope_filters
from models.orm import SessionLocal
from schemas.response import ResponseEnvelope, PaginationMeta
from utils.cache import RedisCache
from config import Config
from utils.query_builder import QueryBuilder
from models.entities import Permission


class PermissionService:
    """Tách CRUD/list permission khỏi DataService để thu hẹp surface."""

    def __init__(
        self,
        perm_repo: Optional[PermissionRepoProtocol] = None,
        cache: Optional[RedisCache] = None,
    ):
        self.perm_repo: PermissionRepoProtocol = perm_repo or PermissionRepository()
        self.cache = cache or RedisCache(ttl_seconds=int(Config.AUTHZ_CACHE_TTL), prefix="uaa:perm:list:v2:")

    def permission_info(self, requester_id: Optional[int], ids: List[int]):
        if not ids:
            return ResponseEnvelope(status="OK", data=[])
        scope_sql, scope_params = data_scope_filters(SessionLocal, requester_id, table_name="permissions")
        extra = (" AND " + scope_sql) if scope_sql else ""
        rows = self.perm_repo.get_permission_info(ids, extra, scope_params or [])
        return ResponseEnvelope(status="OK", data=rows)

    def add_permission(self, code: str, ptype: str, description: Optional[str], url_list: List, data_sets: List):
        try:
            pid = self.perm_repo.insert_permission(code, ptype, description, url_list, data_sets)
            return ResponseEnvelope(status="OK", data={"id": pid})
        except IntegrityError:
            return ResponseEnvelope(status="FAIL", message="Permission code already exists")
        except ValueError as e:
            return ResponseEnvelope(status="FAIL", message=str(e))
        except Exception as e:
            return ResponseEnvelope(status="FAIL", message=str(e))

    def update_permission(self, pid: int, description: Optional[str], ptype: str, url_list: List, data_sets: List):
        try:
            self.perm_repo.update_permission(pid, description, ptype, url_list, data_sets)
            return ResponseEnvelope(status="OK")
        except ValueError as e:
            return ResponseEnvelope(status="FAIL", message=str(e))
        except Exception as e:
            return ResponseEnvelope(status="FAIL", message=str(e))

    def delete_permission(self, pid: int):
        self.perm_repo.delete_permission(pid)
        return ResponseEnvelope(status="OK")

    def list_permissions(self, requester_id: Optional[int], page: int, page_size: int, code: Optional[str], ptype_list: Optional[List[str]]):
        offset = (page - 1) * page_size
        scope_sql, scope_params = data_scope_filters(SessionLocal, requester_id, table_name="permissions")
        qb = QueryBuilder(model=Permission)
        qb.add_ilike("code", code)
        if ptype_list:
            qb.add_any("permission_type", ptype_list)
        qb.add_raw(scope_sql, scope_params or [])
        filters = qb.filters()

        cache_key = None
        if scope_sql is None and scope_params is None:
            cache_key = f"perm:list:{code}:{ptype_list}:{page}:{page_size}"
            cached = self.cache.get_json(cache_key)
            if cached:
                meta = PaginationMeta(page=page, page_size=page_size, total=cached.get("total"), total_row=[{"sum": cached.get("total")}])
                return ResponseEnvelope(status="OK", data=cached.get("rows", []), meta=meta)

        total, rows = self.perm_repo.list_permissions_orm(filters, page_size, offset)
        if cache_key:
            self.cache.set_json(cache_key, {"total": total, "rows": rows})
        meta = PaginationMeta(page=page, page_size=page_size, total=total, total_row=[{"sum": total}])
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def list_data_permissions(self, page: int, page_size: int, code: Optional[str]):
        offset = (page - 1) * page_size
        qb = QueryBuilder(model=Permission)
        qb.add_equals("permission_type", "DATA").add_ilike("code", code)
        filters = qb.filters()

        cache_key = f"perm:data:list:{code}:{page}:{page_size}"
        cached = self.cache.get_json(cache_key)
        if cached:
            meta = PaginationMeta(page=page, page_size=page_size, total=cached.get("total"), total_row=[{"sum": cached.get("total")}])
            return ResponseEnvelope(status="OK", data=cached.get("rows", []), meta=meta)

        total, rows = self.perm_repo.list_permissions_orm(filters, page_size, offset)
        self.cache.set_json(cache_key, {"total": total, "rows": rows})
        meta = PaginationMeta(page=page, page_size=page_size, total=total, total_row=[{"sum": total}])
        return ResponseEnvelope(status="OK", data=rows, meta=meta)

    def public_data_permissions(self, page: int, page_size: int, code: Optional[str]):
        offset = (page - 1) * page_size
        qb = QueryBuilder(model=Permission)
        qb.add_equals("permission_type", "DATA").add_ilike("code", code)
        filters = qb.filters()

        cache_key = f"perm:data:public:{code}:{page}:{page_size}"
        cached = self.cache.get_json(cache_key)
        if cached:
            meta = PaginationMeta(page=page, page_size=page_size, total=cached.get("total"))
            return ResponseEnvelope(status="OK", data=cached.get("rows", []), meta=meta)

        total, rows = self.perm_repo.list_public_data_permissions_orm(filters, page_size, offset)
        self.cache.set_json(cache_key, {"total": total, "rows": rows})
        meta = PaginationMeta(page=page, page_size=page_size, total=total)
        return ResponseEnvelope(status="OK", data=rows, meta=meta)
