"""
Endpoints:
- POST /login
- POST /register
- POST /check_auth_ext
"""

from datetime import datetime
import json

from flask import Blueprint, request
from bson import json_util
import jwt

from config import Config
from utils.http import json_response, validate_body
from schemas.auth import LoginRequest, RegisterRequest
from services.container import auth_service, registration_service
from services.session_service import get_user_session, is_session_user
from schemas.response import ResponseEnvelope

authentication = Blueprint("authentication", __name__)
_auth_service = auth_service()
_registration_service = registration_service()


@authentication.route("/login", methods=["POST"])
@validate_body(LoginRequest)
def login():
    payload: LoginRequest = request.parsed_obj
    success, body, status = _auth_service.login(payload.UserName.strip(), payload.Password)
    token = body.get("token")
    envelope = ResponseEnvelope(
        status="OK" if success else "FAIL",
        message=body.get("message"),
        data={"token": token},
        token=token,  # duy trì tương thích cho frontend cũ đọc trực tiếp
    )
    return json_response(envelope, status=status)


@authentication.route("/register", methods=["POST"])
@validate_body(RegisterRequest)
def register():
    payload: RegisterRequest = request.parsed_obj
    success, body, status = _registration_service.register(
        username=payload.UserName.strip(),
        password=payload.Password,
        name_display=payload.NameDisplay or "",
        requested_roles=payload.Roles,
        requested_role_codes=payload.RoleCodes,
        requested_data_perms=payload.DataPermissions,
        requested_data_perm_codes=payload.DataPermissionCodes,
        requested_set_ids=payload.SetIds,
        reason=payload.Reason,
        ttl_hours=payload.TtlHours,
    )
    token = body.get("token")
    envelope = ResponseEnvelope(
        status="OK" if success else "FAIL",
        message=body.get("message"),
        data={"token": token, "request_status": body.get("request_status")},
        token=token,
    )
    return json_response(envelope, status=status)


@authentication.route("/check_auth_ext", methods=["POST"])
def check_auth_ext():
    jwt_token = request.cookies.get("app_token")
    if not jwt_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            jwt_token = auth_header.split(None, 1)[1]

    if not jwt_token:
        return json_response(ResponseEnvelope(status="FAIL", message="Access is denied"), status=401)

    try:
        auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except Exception:
        return json_response(ResponseEnvelope(status="FAIL", message="Token is invalid"), status=401)

    user_id = auth_info.get("UserId")
    if not is_session_user(user_id):
        return json_response(ResponseEnvelope(status="FAIL", message="Access is denied"), status=401)

    _, username = get_user_session()
    payload = {"UserId": user_id, "UserName": username}
    return json_response(ResponseEnvelope(status="OK", data=payload), status=200)
