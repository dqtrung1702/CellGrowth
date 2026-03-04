import os
import ssl
import redis
from urllib.parse import urlparse, urlunparse
from datetime import timedelta


def _build_redis_url(default_url: str) -> str:
        """
        Compose Redis URL with environment overrides.
        Precedence: PERSON_REDIS_URL -> REDIS_URL -> default_url.
        If PERSON_REDIS_DB is set, replace DB in the URL.
        """
        raw_url = os.getenv("PERSON_REDIS_URL") or os.getenv("REDIS_URL") or default_url
        parsed = urlparse(raw_url)
        db_override = os.getenv("PERSON_REDIS_DB")
        if db_override is not None:
                parsed = parsed._replace(path=f"/{db_override.strip()}")
        return urlunparse(parsed)


def _bool_env(name: str, default: bool) -> bool:
        val = os.getenv(name)
        if val is None:
                return default
        return val.strip().lower() in ("1", "true", "yes", "on")

_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _redis_ssl_kwargs():
        """
        Build SSL kwargs for redis.from_url.
        - PERSON_REDIS_SSL_VERIFY=false disables verification (CERT_NONE).
        - PERSON_REDIS_CA_CERT overrides path to CA file.
        """
        verify = _bool_env("PERSON_REDIS_SSL_VERIFY", True)
        if not verify:
                return {"ssl_cert_reqs": ssl.CERT_NONE}

        ca_cert = os.getenv("PERSON_REDIS_CA_CERT") or os.path.join(_ROOT_DIR, "infra", "redis", "certs", "ca.crt")
        kwargs = {"ssl_cert_reqs": ssl.CERT_REQUIRED}
        kwargs["ssl_ca_certs"] = ca_cert
        return kwargs


class Config(object):
        PERSON_IP = '0.0.0.0'
        PERSON_PORT = 8083
        PERSON_DEBUG_MODE = True

        SECRET_KEY = os.getenv('PERSON_SECRET_KEY', 'ERP-as-Services')
        SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        SESSION_TYPE = 'redis'
        SESSION_COOKIE_NAME = os.getenv('PERSON_SESSION_COOKIE', 'person_session')
        SESSION_KEY_PREFIX = os.getenv('PERSON_SESSION_PREFIX', 'person_sess:')
        SESSION_USE_SIGNER = True
        SESSION_COOKIE_DOMAIN = os.getenv('PERSON_SESSION_DOMAIN')
        SESSION_COOKIE_SECURE = _bool_env('PERSON_SESSION_COOKIE_SECURE', False)
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = os.getenv('PERSON_SESSION_COOKIE_SAMESITE', 'Lax')
        PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv('SESSION_TTL_HOURS', 12)))
        SESSION_REDIS = redis.from_url(
                _build_redis_url('rediss://:123456%40@localhost:6380/2'),
                socket_connect_timeout=2,
                socket_timeout=2,
                **_redis_ssl_kwargs(),
        )

        MONGO_URI = os.getenv('PERSON_MONGO_URI', 'mongodb://admin:admin@localhost:27017/dev?authSource=admin')
        UAA_URL = os.getenv('PERSON_UAA_URL', 'http://localhost:8082/')
