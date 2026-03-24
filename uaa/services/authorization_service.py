import time
from typing import Optional, Tuple, Dict

from sqlalchemy import text

from repositories.permission_repository import PermissionRepository
from repositories.interfaces import PermissionRepoProtocol
from config import Config


class AuthorizationService:
    def __init__(self, perm_repo: Optional[PermissionRepoProtocol] = None, cache_ttl: Optional[int] = None):
        self.perm_repo: PermissionRepoProtocol = perm_repo or PermissionRepository()
        self.cache_ttl = cache_ttl or Config.AUTHZ_CACHE_TTL
        # cache key: (user_id, method, path) -> (allowed: bool, expires_at: float)
        self._cache: Dict[Tuple[int, str, str], Tuple[bool, float]] = {}

    def _cache_get(self, key):
        allowed_exp = self._cache.get(key)
        if not allowed_exp:
            return None
        allowed, expires = allowed_exp
        if expires < time.time():
            self._cache.pop(key, None)
            return None
        return allowed

    def _cache_set(self, key, value: bool):
        self._cache[key] = (value, time.time() + self.cache_ttl)

    def has_url_access(self, user_id: int, path: str, method: str) -> bool:
        key = (user_id, method.upper(), path)
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        try:
            with self.perm_repo.session() as session:
                allowed = session.execute(
                    text(
                        """
                        SELECT 1
                        FROM user_roles ur
                        JOIN role_permissions rp ON rp.role_id = ur.role_id
                        JOIN url_permissions up ON up.permission_id = rp.permission_id
                        WHERE ur.user_id = :uid
                          AND (up.method = '*' OR upper(up.method) = :method)
                          AND (up.url = :path OR :path LIKE up.url)
                        LIMIT 1;
                        """
                    ),
                    {"uid": user_id, "method": method.upper(), "path": path},
                ).first()
                allowed_bool = bool(allowed)
                self._cache_set(key, allowed_bool)
                return allowed_bool
        except Exception:
            return False
