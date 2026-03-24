import json
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import jwt
from sqlalchemy import text

from config import Config
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from repositories.interfaces import UserRepoProtocol, RoleRepoProtocol, PermissionRepoProtocol
from services.password_service import PasswordService
from services.access_request_service import AccessRequestService
from services.session_service import set_user_session


class AuthService:
    def __init__(
        self,
        user_repo: Optional[UserRepoProtocol] = None,
        password_service: Optional[PasswordService] = None,
        role_repo: Optional[RoleRepoProtocol] = None,
        perm_repo: Optional[PermissionRepoProtocol] = None,
        access_request_service: Optional[AccessRequestService] = None,
    ):
        # Prefer ORM-backed repo for auth flows; fallback to legacy if injected/required.
        self.user_repo: UserRepoProtocol = user_repo or UserRepository()
        self.password_service = password_service or PasswordService()
        self.role_repo: RoleRepoProtocol = role_repo or RoleRepository()
        self.perm_repo: PermissionRepoProtocol = perm_repo or PermissionRepository()
        self.access_request_service = access_request_service or AccessRequestService(user_repo=self.user_repo)

    # ---------- helpers ----------
    def _token_payload(self, user_id: int, username: str):
        payload = {
            "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS),
            "UserId": user_id,
            "UserName": username,
        }
        jwt_token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
        token_str = jwt_token if isinstance(jwt_token, str) else jwt_token.decode("utf-8")
        return token_str, payload

    def _ids_from_codes(self, table: str, column: str, codes: List[str]) -> List[int]:
        if not codes:
            return []
        repo = self.role_repo if table == "roles" else self.perm_repo
        with repo.session() as session:
            rows = session.execute(
                text(f"SELECT id FROM {table} WHERE {column} = ANY(:codes);"),
                {"codes": codes},
            ).scalars().all()
            return rows

    # ---------- operations ----------
    def login(self, username: str, password: str) -> Tuple[bool, dict, int]:
        user = self.user_repo.get_by_username(username)
        if not user:
            return False, {"message": "User is incorrect", "status": "FAIL"}, 200
        if user.get("userlocked"):
            return False, {"message": "User is locked", "status": "FAIL"}, 200
        if not self.password_service.verify(user.get("password"), password):
            return False, {"message": "Password is incorrect", "status": "FAIL"}, 200

        self.user_repo.update_last_signon(user["id"])
        token_str, _ = self._token_payload(user["id"], username)
        set_user_session(user["id"], username)
        return True, {"token": token_str, "status": "OK", "UserId": user["id"]}, 200

    def register(
        self,
        username: str,
        password: str,
        name_display: str = "",
        requested_roles: Optional[List[int]] = None,
        requested_role_codes: Optional[List[str]] = None,
        requested_data_perms: Optional[List[int]] = None,
        requested_data_perm_codes: Optional[List[str]] = None,
        requested_set_ids: Optional[List[int]] = None,
        reason: Optional[str] = None,
        ttl_hours: Optional[int] = None,
    ) -> Tuple[bool, dict, int]:
        if self.user_repo.get_by_username(username):
            return False, {"message": "UserName is existed", "status": "FAIL"}, 200
        hashed = self.password_service.hash(password)
        user_id = self.user_repo.insert_user(username, hashed, name_display)

        requested_roles = requested_roles or []
        requested_role_codes = requested_role_codes or []
        requested_data_perms = requested_data_perms or []
        requested_data_perm_codes = requested_data_perm_codes or []
        requested_set_ids = requested_set_ids or []

        # resolve codes -> ids
        if requested_role_codes:
            requested_roles.extend(self._ids_from_codes("roles", "code", requested_role_codes))
        if requested_data_perm_codes:
            requested_data_perms.extend(self._ids_from_codes("permissions", "code", requested_data_perm_codes))

        has_request = requested_roles or requested_data_perms or requested_set_ids
        if has_request:
            self.access_request_service.create(
                user_id,
                username,
                "DATA" if requested_data_perms else "ROLE",
                reason,
                ttl_hours,
                requested_roles,
                requested_data_perms,
            )

        token_str, _ = self._token_payload(user_id, username)
        set_user_session(user_id, username)
        return True, {
            "token": token_str,
            "status": "OK",
            "UserId": user_id,
            "request_status": "SUBMITTED" if has_request else None,
        }, 201
