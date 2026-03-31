from flask import Blueprint, request

from utils.http import json_response, validate_body
from utils.token import current_user_id
from schemas.response import ResponseEnvelope
from schemas.mfa import EnrollTOTPRequest, VerifyTOTPRequest, DisableTOTPRequest
from services.container import totp_service
from services.session_service import set_user_session
from repositories.user_repository import UserRepository

mfa_bp = Blueprint("mfa", __name__)
_totp = totp_service()
_user_repo = UserRepository()


def _user_id_or_current(payload_uid):
    return payload_uid or current_user_id()


@mfa_bp.route("/mfa/totp/enroll", methods=["POST"])
@validate_body(EnrollTOTPRequest)
def enroll_totp():
    payload: EnrollTOTPRequest = request.parsed_obj
    uid = _user_id_or_current(payload.UserId)
    if not uid:
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)
    data = _totp.enroll(uid)
    return json_response(ResponseEnvelope(status="OK", data=data))


@mfa_bp.route("/mfa/totp/verify", methods=["POST"])
@validate_body(VerifyTOTPRequest)
def verify_totp():
    payload: VerifyTOTPRequest = request.parsed_obj
    uid = _user_id_or_current(payload.UserId)
    if not uid:
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)
    ok = _totp.verify(uid, payload.Code)
    status = "OK" if ok else "FAIL"
    return json_response(ResponseEnvelope(status=status, message=None if ok else "Invalid code"), status=200 if ok else 400)


@mfa_bp.route("/mfa/totp/verify_login", methods=["POST"])
@validate_body(VerifyTOTPRequest)
def verify_totp_login():
    payload: VerifyTOTPRequest = request.parsed_obj
    # mfa_token được frontend gửi kèm (header X-MFA-Token hoặc query/body mfa_token)
    mfa_token = request.headers.get("X-MFA-Token") or request.args.get("mfa_token") or request.json.get("mfa_token", None)
    if not mfa_token:
        return json_response(ResponseEnvelope(status="FAIL", message="Missing mfa_token"), status=400)
    token_bundle = _totp.verify_and_issue(mfa_token, payload.Code)
    if not token_bundle:
        return json_response(ResponseEnvelope(status="FAIL", message="Invalid code or token")), 400

    # kiểm tra user chưa bị khóa sau bước 1
    uid = token_bundle["payload"]["UserId"]
    user = _user_repo.get_by_id(uid) if hasattr(_user_repo, "get_by_id") else None
    if user and user.get("userlocked"):
        return json_response(ResponseEnvelope(status="FAIL", message="User is locked"), status=403)

    # set session cho phiên hiện tại
    set_user_session(uid, token_bundle["payload"]["UserName"])
    token_str = token_bundle["token"]
    return json_response(ResponseEnvelope(status="OK", data={"token": token_str}, token=token_str))


@mfa_bp.route("/mfa/totp/disable", methods=["POST"])
@validate_body(DisableTOTPRequest)
def disable_totp():
    payload: DisableTOTPRequest = request.parsed_obj
    uid = _user_id_or_current(payload.UserId)
    if not uid:
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)
    _totp.disable(uid)
    return json_response(ResponseEnvelope(status="OK"))


__all__ = ["mfa_bp"]
