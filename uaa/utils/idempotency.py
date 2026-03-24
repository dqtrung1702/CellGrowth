import functools
from typing import Callable, Any, Optional, Tuple
import uuid

from flask import request, g

from config import Config
from utils.cache import RedisCache
from services.container import redis_client


def idempotency(ttl_seconds: Optional[int] = None):
    """
    Decorator: nếu header Idempotency-Key có mặt, trả cùng response cho cùng key+path trong TTL.
    Lưu response (body, status) vào Redis.
    """
    ttl = ttl_seconds or Config.IDEMPOTENCY_TTL_SECONDS
    cache = RedisCache(client=redis_client(), ttl_seconds=ttl, prefix="uaa:idemp:")

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = request.headers.get("Idempotency-Key")
            path = request.path
            if not key:
                return fn(*args, **kwargs)

            cache_key = f"{path}:{key}"
            cached = cache.get_json(cache_key)
            if cached:
                return cached["body"], cached.get("status", 200), cached.get("headers", {})

            resp = fn(*args, **kwargs)

            # Flask response tuple could be (body,status) or (body,status,headers)
            if isinstance(resp, tuple):
                if len(resp) == 2:
                    body, status = resp
                    headers = {}
                else:
                    body, status, headers = resp
            else:
                body, status, headers = resp, 200, {}

            cache.set_json(cache_key, {"body": body, "status": status, "headers": headers})
            return resp

        return wrapper

    return decorator


def ensure_request_id():
    """Đặt g.request_id từ header X-Request-ID hoặc sinh mới."""
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    g.request_id = rid
    return rid
