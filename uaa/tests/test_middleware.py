import os
import jwt

# Skip redis health check when importing main app for tests
os.environ.setdefault("UAA_SKIP_REDIS_HEALTHCHECK", "1")
os.environ.setdefault("UAA_SKIP_DB_INIT", "1")

import main
from config import Config


class DummyAuthz:
    def __init__(self, allowed: bool):
        self.allowed = allowed

    def has_url_access(self, user_id, path, method):
        return self.allowed


def _make_token(user_id=1):
    token = jwt.encode({"UserId": user_id}, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def test_public_endpoint_skips_authz(monkeypatch):
    app = main.app
    main._authz = DummyAuthz(False)
    client = app.test_client()
    resp = client.get("/status")
    # middleware should not block; underlying route may 404 but not 401/403
    assert resp.status_code in (200, 404)


def test_protected_endpoint_requires_token(monkeypatch):
    app = main.app
    main._authz = DummyAuthz(True)
    client = app.test_client()
    resp = client.get("/private-path-not-exist")
    assert resp.status_code == 401


def test_protected_endpoint_needs_authorization(monkeypatch):
    app = main.app
    main._authz = DummyAuthz(False)
    client = app.test_client()
    token = _make_token()
    resp = client.get("/private-path-not-exist", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
