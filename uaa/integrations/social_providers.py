"""Lightweight OAuth2 provider clients.

Google is the only provider registered by default; Facebook/Zalo classes are
kept for reference but not wired into the default provider map.

These clients intentionally avoid extra dependencies; they rely on simple
`requests` calls to exchange code->token and fetch user profile.
They return a normalized SocialProfile dataclass used by SocialAuthService.
"""
from dataclasses import dataclass
from typing import Dict, List
import requests


class SocialAuthError(Exception):
    pass


@dataclass
class SocialProfile:
    provider: str
    external_id: str
    email: str
    name: str
    avatar: str


class IdentityProviderClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def build_authorize_url(self, state: str) -> str:
        raise NotImplementedError

    def exchange_code(self, code: str) -> Dict:
        raise NotImplementedError

    def fetch_profile(self, token_resp: Dict) -> SocialProfile:
        raise NotImplementedError


class GoogleClient(IdentityProviderClient):
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"

    def build_authorize_url(self, state: str) -> str:
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Dict:
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            resp = requests.post(self.token_url, data=data, timeout=5)
        except requests.RequestException as exc:
            raise SocialAuthError(f"Google token error: {exc}") from exc
        if resp.status_code != 200:
            raise SocialAuthError(f"Google token error: {resp.text}")
        return resp.json()

    def fetch_profile(self, token_resp: Dict) -> SocialProfile:
        access_token = token_resp.get("access_token")
        if not access_token:
            raise SocialAuthError("Google token missing access_token")
        try:
            resp = requests.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=5,
            )
        except requests.RequestException as exc:
            raise SocialAuthError(f"Google userinfo error: {exc}") from exc
        if resp.status_code != 200:
            raise SocialAuthError(f"Google userinfo error: {resp.text}")
        data = resp.json()
        return SocialProfile(
            provider="google",
            external_id=data.get("sub") or data.get("id"),
            email=data.get("email"),
            name=data.get("name") or data.get("given_name"),
            avatar=data.get("picture"),
        )


class FacebookClient(IdentityProviderClient):
    auth_url = "https://www.facebook.com/v12.0/dialog/oauth"
    token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
    userinfo_url = "https://graph.facebook.com/me"

    def build_authorize_url(self, state: str) -> str:
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "scope": "email,public_profile",
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Dict:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        try:
            resp = requests.get(self.token_url, params=params, timeout=5)
        except requests.RequestException as exc:
            raise SocialAuthError(f"Facebook token error: {exc}") from exc
        if resp.status_code != 200:
            raise SocialAuthError(f"Facebook token error: {resp.text}")
        return resp.json()

    def fetch_profile(self, token_resp: Dict) -> SocialProfile:
        access_token = token_resp.get("access_token")
        if not access_token:
            raise SocialAuthError("Facebook token missing access_token")
        params = {"fields": "id,name,email,picture", "access_token": access_token}
        try:
            resp = requests.get(self.userinfo_url, params=params, timeout=5)
        except requests.RequestException as exc:
            raise SocialAuthError(f"Facebook userinfo error: {exc}") from exc
        if resp.status_code != 200:
            raise SocialAuthError(f"Facebook userinfo error: {resp.text}")
        data = resp.json()
        picture = None
        if isinstance(data.get("picture"), dict):
            picture = data.get("picture", {}).get("data", {}).get("url")
        return SocialProfile(
            provider="facebook",
            external_id=data.get("id"),
            email=data.get("email"),
            name=data.get("name"),
            avatar=picture,
        )


class ZaloClient(IdentityProviderClient):
    auth_url = "https://oauth.zaloapp.com/v4/permission"
    token_url = "https://oauth.zaloapp.com/v4/access_token"
    userinfo_url = "https://graph.zalo.me/v2.0/me"

    def build_authorize_url(self, state: str) -> str:
        from urllib.parse import urlencode

        params = {
            "app_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "code_challenge": "",
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Dict:
        data = {
            "app_id": self.client_id,
            "app_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            resp = requests.post(self.token_url, data=data, timeout=5)
        except requests.RequestException as exc:
            raise SocialAuthError(f"Zalo token error: {exc}") from exc
        if resp.status_code != 200:
            raise SocialAuthError(f"Zalo token error: {resp.text}")
        return resp.json()

    def fetch_profile(self, token_resp: Dict) -> SocialProfile:
        access_token = token_resp.get("access_token")
        if not access_token:
            raise SocialAuthError("Zalo token missing access_token")
        params = {"access_token": access_token, "fields": "id,name,picture"}
        try:
            resp = requests.get(self.userinfo_url, params=params, timeout=5)
        except requests.RequestException as exc:
            raise SocialAuthError(f"Zalo userinfo error: {exc}") from exc
        if resp.status_code != 200:
            raise SocialAuthError(f"Zalo userinfo error: {resp.text}")
        data = resp.json()
        avatar = None
        if isinstance(data.get("picture"), dict):
            avatar = data.get("picture", {}).get("data", {}).get("url")
        return SocialProfile(
            provider="zalo",
            external_id=str(data.get("id")),
            email=data.get("email"),
            name=data.get("name"),
            avatar=avatar,
        )


def build_default_provider_map(db_configs: List[Dict] | None = None) -> Dict[str, IdentityProviderClient]:
    """
    Build provider map ưu tiên cấu hình lấy từ DB (db_configs).
    db_configs: list dict {provider, client_id, client_secret, redirect_uri, scopes}
    Nếu DB không có provider, map sẽ rỗng và SocialAuthService sẽ báo thiếu cấu hình.
    """
    providers: Dict[str, IdentityProviderClient] = {}
    for cfg in db_configs or []:
        provider = (cfg.get("provider") or "").lower()
        if provider == "google":
            providers["google"] = GoogleClient(cfg["client_id"], cfg["client_secret"], cfg["redirect_uri"])
    return providers
