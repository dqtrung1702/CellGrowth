import os
import ssl
import redis
from urllib.parse import urlparse, urlunparse
from datetime import timedelta


def _build_redis_url(default_url: str) -> str:
        """Return the hard-coded Redis URL; ignore OS environment overrides."""
        return default_url


def _bool_env(name: str, default: bool) -> bool:
        val = os.getenv(name)
        if val is None:
                return default
        return val.strip().lower() in ("1", "true", "yes", "on")


_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _redis_ssl_kwargs():
        """
        Build SSL kwargs for redis.from_url.
        - UAA_REDIS_SSL_VERIFY=false disables verification (CERT_NONE).
        - UAA_REDIS_CA_CERT overrides path to CA file; default points to infra/redis/certs/ca.crt.
        """
        verify = _bool_env("UAA_REDIS_SSL_VERIFY", True)
        if not verify:
                return {"ssl_cert_reqs": ssl.CERT_NONE}

        ca_cert = os.getenv("UAA_REDIS_CA_CERT") or os.path.join(_ROOT_DIR, "infra", "redis", "certs", "ca.crt")
        return {"ssl_cert_reqs": ssl.CERT_REQUIRED, "ssl_ca_certs": ca_cert}


class Config(object):
        UAA_IP = '0.0.0.0'
        UAA_PORT = 8082
        UAA_DEBUG_MODE = True

        # Pagination + authz config
        DEFAULT_PAGE = int(os.getenv('UAA_DEFAULT_PAGE', 1))
        DEFAULT_PAGE_SIZE = int(os.getenv('UAA_DEFAULT_PAGE_SIZE', 10))
        MAX_PAGE_SIZE = int(os.getenv('UAA_MAX_PAGE_SIZE', 200))
        PUBLIC_ENDPOINTS = set(
                filter(
                        None,
                        (os.getenv(
                                'UAA_PUBLIC_ENDPOINTS',
                                '/login,/register,/status,/health,/ping,/favicon.ico,/getPageByUser,/getDataSetByUser,/publicRoleList,/publicPermissionList,/docs,/openapi.yaml',
                        ).split(',')),
                )
        )
        PUBLIC_PREFIXES = tuple(
                filter(
                        None,
                        os.getenv('UAA_PUBLIC_PREFIXES', '/status,/health,/static,/swagger').split(','),
                )
        )

        POSTGRES_HOST = "127.0.0.1"
        POSTGRES_PORT = "5432"
        POSTGRES_DB = "dev"
        POSTGRES_USERNAME = "admin"
        POSTGRES_PASSWORD = "admin"
        POSTGRES_OPTIONS = "-c search_path=dbo,uaa"
        POSTGRES_MINCONN= 1
        POSTGRES_MAXCONN= 10

        SECRET_KEY = os.getenv('UAA_SECRET_KEY', 'ERP-as-Services')
        SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        SESSION_TYPE = 'redis'
        SESSION_COOKIE_NAME = os.getenv('UAA_SESSION_COOKIE', 'uaa_session')
        SESSION_KEY_PREFIX = os.getenv('UAA_SESSION_PREFIX', 'uaa_sess:')
        SESSION_USE_SIGNER = True
        SESSION_COOKIE_DOMAIN = os.getenv('UAA_SESSION_DOMAIN')
        SESSION_COOKIE_SECURE = _bool_env('UAA_SESSION_COOKIE_SECURE', False)
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = os.getenv('UAA_SESSION_COOKIE_SAMESITE', 'Lax')
        PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv('SESSION_TTL_HOURS', 12)))
        SESSION_REDIS = redis.from_url(
                _build_redis_url('rediss://:123456%40@localhost:6380/0'),
                socket_connect_timeout=2,
                socket_timeout=2,
                **_redis_ssl_kwargs(),
        )

        JWT_SECRET = os.getenv('UAA_JWT_SECRET', '$2a$12$hUXgiU2qN/ELnVASgsti1ujEZVbGtpeyPEkddJR4vbrnfSyzdaJaW')
        JWT_ALGORITHM = 'HS256'
        JWT_EXP_DELTA_SECONDS = int(os.getenv('JWT_EXP_SECONDS', 6000000))

        # Social login configuration
        SOCIAL_CALLBACK_BASE = os.getenv('UAA_SOCIAL_CALLBACK_BASE', UAA_URL.rstrip('/'))
        SOCIAL_DEFAULT_ROLE_CODES = [c for c in os.getenv('UAA_SOCIAL_DEFAULT_ROLES', '').split(',') if c]
        SOCIAL_DEFAULT_DATA_PERM_CODES = [c for c in os.getenv('UAA_SOCIAL_DEFAULT_DATA_PERMS', '').split(',') if c]
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
        GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
        GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', f"{SOCIAL_CALLBACK_BASE}/auth/google/callback")
        FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID', '')
        FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET', '')
        FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI', f"{SOCIAL_CALLBACK_BASE}/auth/facebook/callback")
        ZALO_CLIENT_ID = os.getenv('ZALO_CLIENT_ID', '')
        ZALO_CLIENT_SECRET = os.getenv('ZALO_CLIENT_SECRET', '')
        ZALO_REDIRECT_URI = os.getenv('ZALO_REDIRECT_URI', f"{SOCIAL_CALLBACK_BASE}/auth/zalo/callback")
        # Authorization cache (URL-permission) TTL seconds
        AUTHZ_CACHE_TTL = int(os.getenv('UAA_AUTHZ_CACHE_TTL', 300))
        IDEMPOTENCY_TTL_SECONDS = int(os.getenv('UAA_IDEMPOTENCY_TTL', 600))
        AUDIT_LOG_PATH = os.getenv('UAA_AUDIT_LOG_PATH', os.path.abspath(os.path.join(_ROOT_DIR, "..", "logs", "audit.log")))

        SQLALCHEMY_DATABASE_URI = os.getenv(
                'UAA_DATABASE_URI',
                'postgresql://admin:admin@localhost:5432/dev?options=-c%20search_path=uaa'
        )
        SQLALCHEMY_TRACK_MODIFICATIONS = True

        UAA_URL = os.getenv('UAA_URL', 'http://localhost:8082/')
        BOOLEAN = {'False':False,'True':True,'false':False,'true':True,'on':True,'off':False}
