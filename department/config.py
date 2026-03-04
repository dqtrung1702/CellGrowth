import os
import redis
from urllib.parse import urlparse, urlunparse
from datetime import timedelta


def _build_redis_url(default_url: str) -> str:
        """
        Compose Redis URL with environment overrides.
        Precedence: DEPT_REDIS_URL -> REDIS_URL -> default_url.
        If DEPT_REDIS_DB is set, replace DB in the URL.
        """
        raw_url = os.getenv("DEPT_REDIS_URL") or os.getenv("REDIS_URL") or default_url
        parsed = urlparse(raw_url)
        db_override = os.getenv("DEPT_REDIS_DB")
        if db_override is not None:
                parsed = parsed._replace(path=f"/{db_override.strip()}")
        return urlunparse(parsed)


def _bool_env(name: str, default: bool) -> bool:
        val = os.getenv(name)
        if val is None:
                return default
        return val.strip().lower() in ("1", "true", "yes", "on")


class Config(object):
        DEPT_IP = '0.0.0.0'
        DEPT_PORT = 8082
        DEPT_DEBUG_MODE = True

        SECRET_KEY = os.getenv('DEPT_SECRET_KEY', 'ERP-as-Services')
        SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        SESSION_TYPE = 'redis'
        SESSION_COOKIE_NAME = os.getenv('DEPT_SESSION_COOKIE', 'dept_session')
        SESSION_KEY_PREFIX = os.getenv('DEPT_SESSION_PREFIX', 'dept_sess:')
        SESSION_USE_SIGNER = True
        SESSION_COOKIE_DOMAIN = os.getenv('DEPT_SESSION_DOMAIN')
        SESSION_COOKIE_SECURE = _bool_env('DEPT_SESSION_COOKIE_SECURE', False)
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = os.getenv('DEPT_SESSION_COOKIE_SAMESITE', 'Lax')
        PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv('SESSION_TTL_HOURS', 12)))
        SESSION_REDIS = redis.from_url(
                _build_redis_url('rediss://:change-me@localhost:6380/1'),
                socket_connect_timeout=2,
                socket_timeout=2,
        )

        JWT_SECRET = os.getenv('DEPT_JWT_SECRET', 'ERP-as-Services')
        JWT_ALGORITHM = 'HS256'
        JWT_EXP_DELTA_SECONDS = int(os.getenv('JWT_EXP_SECONDS', 6000000))

        MONGO_URI = os.getenv('DEPT_MONGO_URI', 'mongodb://root:pass12345@10.14.119.41:27018/test?authSource=admin')
        UAA_URL = os.getenv('DEPT_UAA_URL', 'http://localhost:8081/')
