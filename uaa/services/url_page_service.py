from typing import List

from repositories.permission_repository import PermissionRepository
from repositories.interfaces import PermissionRepoProtocol
from schemas.response import ResponseEnvelope


class UrlPageService:
    """Tách phần URL/Page permission khỏi PermissionService."""

    def __init__(self, perm_repo: PermissionRepoProtocol = None):
        self.perm_repo = perm_repo or PermissionRepository()

    def urls_by_permission(self, pid: int):
        rows = self.perm_repo.list_url_by_permission(pid)
        return ResponseEnvelope(status="OK", data=[dict(r) for r in rows])

    def urls_by_permission_list(self, perms: List):
        if not perms:
            return ResponseEnvelope(status="OK", data=[])
        perm_ids = []
        perm_codes = []
        for p in perms:
            try:
                perm_ids.append(int(p))
            except Exception:
                if p is not None:
                    perm_codes.append(str(p))
        rows = self.perm_repo.list_urls_by_permissions(perm_ids, perm_codes)
        return ResponseEnvelope(status="OK", data=[dict(r) for r in rows])

    def pages_by_user(self, uid: int):
        rows = self.perm_repo.list_pages_by_user(uid)
        return ResponseEnvelope(status="OK", data=[dict(r) for r in rows])
