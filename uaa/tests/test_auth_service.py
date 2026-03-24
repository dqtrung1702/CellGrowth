import jwt
import pytest

from services.auth_service import AuthService
from services.password_service import PasswordService


class FakeUserRepo:
    def __init__(self):
        self.updated = False
        self.created = False
        self.user = {"id": 1, "username": "good", "password": b"secret", "userlocked": False}

    def get_by_username(self, username):
        if username == "good":
            return self.user
        if username == "locked":
            locked = self.user.copy()
            locked["userlocked"] = True
            return locked
        return None

    def update_last_signon(self, user_id):
        self.updated = True

    def insert_user(self, username, password_hash, name_display):
        self.created = True
        return 99


class FakePasswordService(PasswordService):
    def verify(self, stored, provided: str) -> bool:  # type: ignore[override]
        return provided == "secret"

    def hash(self, plain: str):
        return plain.encode()


class FakeAccessRequestService:
    def __init__(self):
        self.created = False
        self.payload = None

    def create(self, requester_id, username, req_type, reason, ttl_hours, roles, data_perms, set_ids):
        self.created = True
        self.payload = (requester_id, username, req_type, reason, ttl_hours, roles, data_perms, set_ids)
        return 1


def test_login_success_and_fail():
    auth = AuthService(user_repo=FakeUserRepo(), password_service=FakePasswordService(), access_request_service=FakeAccessRequestService())
    ok, body, status = auth.login("good", "secret")
    assert ok is True
    assert status == 200
    assert "token" in body

    ok, body, status = auth.login("good", "wrong")
    assert ok is False
    assert status == 200


def test_register_triggers_access_request_when_roles():
    fake_ar = FakeAccessRequestService()
    auth = AuthService(user_repo=FakeUserRepo(), password_service=FakePasswordService(), access_request_service=fake_ar)
    ok, body, status = auth.register(
        username="newuser",
        password="secret",
        requested_roles=[1, 2],
        reason="need access",
    )
    assert ok is True
    assert status == 201
    assert fake_ar.created is True
    assert fake_ar.payload[0] == 99  # requester_id returned by insert_user
