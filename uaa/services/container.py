"""
Đơn giản hoá Dependency Injection cho controllers/services.
Sử dụng singleton nhẹ dựa trên factory, dễ mock trong test.
"""
from typing import Callable, TypeVar, Dict, Any

from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from repositories.permission_repository import PermissionRepository
from repositories.set_repository import SetRepository
from repositories.access_request_repository import AccessRequestRepository
from models.orm import SessionLocal, configure_engine
from utils.cache import RedisCache
from config import Config
from services.auth_service import AuthService
from services.registration_service import RegistrationService
from services.access_request_service import AccessRequestService
from services.role_service import RoleService
from services.user_service import UserService
from services.data_service import DataService
from services.permission_service import PermissionService
from services.url_page_service import UrlPageService
from services.set_service import SetService
from services.access_request_approval_service import AccessRequestApprovalService
from services.social_auth_service import SocialAuthService
from services.social_provider_config_service import SocialProviderConfigService
from integrations.social_providers import build_default_provider_map

T = TypeVar("T")


class Container:
    _singletons: Dict[str, Any] = {}

    @classmethod
    def get(cls, key: str, factory: Callable[[], T]) -> T:
        if key not in cls._singletons:
            cls._singletons[key] = factory()
        return cls._singletons[key]


# Factories
def auth_service() -> AuthService:
    return Container.get("auth_service", lambda: AuthService())


def registration_service() -> RegistrationService:
    return Container.get("registration_service", lambda: RegistrationService())


def role_service() -> RoleService:
    return Container.get("role_service", lambda: RoleService())


def user_service() -> UserService:
    return Container.get("user_service", lambda: UserService())


def data_service() -> DataService:
    return Container.get(
        "data_service",
        lambda: DataService(
            perm_repo=PermissionRepository(),
            cache=RedisCache(client=redis_client()),
        ),
    )


def permission_service() -> PermissionService:
    return Container.get(
        "permission_service",
        lambda: PermissionService(PermissionRepository(), RedisCache(client=redis_client())),
    )


def url_page_service() -> UrlPageService:
    return Container.get(
        "url_page_service",
        lambda: UrlPageService(PermissionRepository()),
    )


def set_service() -> SetService:
    return Container.get("set_service", lambda: SetService())


def access_request_service() -> AccessRequestService:
    return Container.get(
        "access_request_service",
        lambda: AccessRequestService(AccessRequestRepository(), UserRepository()),
    )

def access_request_approval_service() -> AccessRequestApprovalService:
    return Container.get(
        "access_request_approval_service",
        lambda: AccessRequestApprovalService(AccessRequestRepository(), UserRepository()),
    )

def social_auth_service() -> SocialAuthService:
    return Container.get(
        "social_auth_service",
        lambda: SocialAuthService(
            user_repo=UserRepository(),
            role_repo=RoleRepository(),
            perm_repo=PermissionRepository(),
            identity_repo=UserIdentityRepository(),
            providers=build_default_provider_map(Config, social_provider_config_service().list_enabled()),
        ),
    )

def social_provider_config_service() -> SocialProviderConfigService:
    return Container.get(
        "social_provider_config_service",
        lambda: SocialProviderConfigService(cache=RedisCache(client=redis_client())),
    )


# ---- Infra clients ----
def db_session_factory():
    return Container.get("db_session_factory", lambda: SessionLocal)


def redis_client():
    return Container.get("redis_client", lambda: Config.SESSION_REDIS)

# Configure engine at import time using Config, but can be overridden in tests by calling configure_engine manually then clearing cache.
configure_engine(Config.SQLALCHEMY_DATABASE_URI)
