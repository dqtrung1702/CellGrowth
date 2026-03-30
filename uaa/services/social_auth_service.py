from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import jwt

from config import Config
from integrations.social_providers import (
    SocialAuthError,
    SocialProfile,
    build_default_provider_map,
)
from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from repositories.user_identity_repository import UserIdentityRepository
from repositories.interfaces import UserRepoProtocol, RoleRepoProtocol, PermissionRepoProtocol, UserIdentityRepoProtocol
from services.password_service import PasswordService
from services.session_service import set_user_session
from models.entities import Role, Permission


@dataclass
class SocialAuthResult:
    user_id: int
    username: str
    token: str
    payload: Dict


class SocialAuthService:
    def __init__(
        self,
        user_repo: Optional[UserRepoProtocol] = None,
        role_repo: Optional[RoleRepoProtocol] = None,
        perm_repo: Optional[PermissionRepoProtocol] = None,
        identity_repo: Optional[UserIdentityRepoProtocol] = None,
        providers: Optional[Dict] = None,
        password_service: Optional[PasswordService] = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.role_repo = role_repo or RoleRepository()
        self.perm_repo = perm_repo or PermissionRepository()
        self.identity_repo = identity_repo or UserIdentityRepository()
        self.providers = providers or build_default_provider_map([])
        self.password_service = password_service or PasswordService()

    # ---- public API ----
    def build_authorize_url(self, provider: str, state: str) -> str:
        client = self._get_client(provider)
        self._ensure_configured(client)
        return client.build_authorize_url(state)

    def handle_callback(self, provider: str, code: str) -> SocialAuthResult:
        client = self._get_client(provider)
        self._ensure_configured(client)
        token_resp = client.exchange_code(code)
        profile = client.fetch_profile(token_resp)

        # 1. resolve user from identity mapping
        identity = self.identity_repo.find_by_provider_external(provider, profile.external_id)
        user_id = None
        username = None
        if identity:
            user_id = identity["user_id"]
            username = self.user_repo.get_username(user_id)
        else:
            # 2. resolve by email
            user_by_email = self.user_repo.get_by_email(profile.email)
            user_id = user_by_email.get("id") if user_by_email else None
            username = user_by_email.get("username") if user_by_email else None
            if user_id and not identity:
                # attach identity to existing user
                self.identity_repo.create_identity(
                    user_id=user_id,
                    provider=provider,
                    external_id=profile.external_id,
                    email=profile.email,
                    display_name=profile.name,
                    avatar_url=profile.avatar,
                    tokens_json=token_resp,
                )

        if not user_id:
            # 3. create new user
            username = profile.email or f"{provider}_{profile.external_id}"
            # ensure unique username by appending timestamp if needed
            suffix = 1
            base_username = username
            while self.user_repo.get_by_username(username):
                suffix += 1
                username = f"{base_username}_{suffix}"
            random_password = self.password_service.hash("social-login-placeholder")
            user_id = self.user_repo.insert_user(username=username, password_hash=random_password, name_display=profile.name or username)

            # assign default roles/data permissions if configured
            self._assign_defaults(user_id)

            self.identity_repo.create_identity(
                user_id=user_id,
                provider=provider,
                external_id=profile.external_id,
                email=profile.email,
                display_name=profile.name,
                avatar_url=profile.avatar,
                tokens_json=token_resp,
            )

        username = username or profile.email or f"{provider}_{profile.external_id}"
        token_str, payload = self._issue_token(user_id, username)
        set_user_session(user_id, username)
        return SocialAuthResult(user_id=user_id, username=username, token=token_str, payload=payload)

    # ---- helpers ----
    def _get_client(self, provider: str):
        key = provider.lower() if provider else provider
        client = self.providers.get(key) if self.providers else None
        if not client:
            raise SocialAuthError(f"Unsupported provider {provider}")
        return client

    def _issue_token(self, user_id: int, username: str) -> Tuple[str, Dict]:
        payload = {
            "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS),
            "UserId": user_id,
            "UserName": username,
        }
        jwt_token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
        token_str = jwt_token if isinstance(jwt_token, str) else jwt_token.decode("utf-8")
        return token_str, payload

    def _assign_defaults(self, user_id: int):
        # roles
        if Config.SOCIAL_DEFAULT_ROLE_CODES:
            role_ids = self._ids_from_codes(Role, Config.SOCIAL_DEFAULT_ROLE_CODES)
            if role_ids:
                self.user_repo.add_roles(user_id, role_ids)
        # data permission
        if Config.SOCIAL_DEFAULT_DATA_PERM_CODES:
            perm_ids = self._ids_from_codes(Permission, Config.SOCIAL_DEFAULT_DATA_PERM_CODES)
            if perm_ids:
                self.user_repo.set_data_permission(user_id, perm_ids[0])

    def _ids_from_codes(self, model, codes):
        if not codes:
            return []
        repo = self.role_repo if model is Role else self.perm_repo
        with repo.session() as session:  # type: ignore
            return session.query(model.id).filter(model.code.in_(codes)).scalars().all()

    def _ensure_configured(self, client):
        if not getattr(client, "client_id", None) or not getattr(client, "client_secret", None):
            raise SocialAuthError("Provider is not configured (missing client_id/client_secret)")
