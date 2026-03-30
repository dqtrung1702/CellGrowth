from typing import Dict, Optional

from repositories.social_provider_repository import SocialProviderRepository
from utils.cache import RedisCache
from utils.secret_cipher import decrypt_secret, master_key_from_env
from config import Config


class SocialProviderConfigService:
    def __init__(self, repo: Optional[SocialProviderRepository] = None, cache: Optional[RedisCache] = None):
        self.repo = repo or SocialProviderRepository()
        self.cache = cache or RedisCache(client=Config.SESSION_REDIS, prefix="uaa:social_cfg:", ttl_seconds=300)
        self.master_key = master_key_from_env()

    def get(self, provider: str) -> Optional[Dict]:
        provider = (provider or "").lower()
        if not provider:
            return None
        cache_key = provider
        cached = self.cache.get_json(cache_key)
        if cached:
            return cached
        row = self.repo.get_by_provider(provider)
        if not row or not row.get("enabled"):
            return None
        try:
            secret = decrypt_secret(row["client_secret_enc"], self.master_key)
        except Exception:
            return None
        cfg = {
            "provider": provider,
            "client_id": row["client_id"],
            "client_secret": secret,
            "redirect_uri": row["redirect_uri"],
            "scopes": row.get("scopes") or "openid email profile",
        }
        self.cache.set_json(cache_key, cfg)
        return cfg

    def list_enabled(self):
        rows = self.repo.list_enabled()
        items = []
        for r in rows:
            try:
                secret = decrypt_secret(r["client_secret_enc"], self.master_key)
            except Exception:
                continue
            items.append(
                {
                    "provider": r["provider"],
                    "client_id": r["client_id"],
                    "client_secret": secret,
                    "redirect_uri": r["redirect_uri"],
                    "scopes": r.get("scopes") or "openid email profile",
                }
            )
        return items
