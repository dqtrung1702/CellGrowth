import json
import time
from typing import Optional

import redis

from config import Config


class RedisCache:
    """Cache đơn giản dựa trên redis client đã có trong Config (SESSION_REDIS)."""

    def __init__(self, client: Optional[redis.Redis] = None, ttl_seconds: int = 120, prefix: str = "uaa:cache:"):
        if client is None:
            try:
                from services.container import redis_client

                self.client = redis_client()
            except Exception:
                self.client = Config.SESSION_REDIS
        else:
            self.client = client
        self.ttl = ttl_seconds
        self.prefix = prefix

    def _k(self, key: str) -> str:
        return f"{self.prefix}{key}"

    def get_json(self, key: str):
        raw = self.client.get(self._k(key))
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def set_json(self, key: str, value, ttl: Optional[int] = None):
        def _default(o):
            import datetime

            if isinstance(o, (datetime.datetime, datetime.date)):
                return o.isoformat()
            raise TypeError

        self.client.setex(self._k(key), ttl or self.ttl, json.dumps(value, default=_default))

    def delete_prefix(self, prefix: str):
        """Xóa theo prefix (scan) - dùng khi invalidation sau khi ghi."""
        full_prefix = self._k(prefix)
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor=cursor, match=f"{full_prefix}*")
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break
