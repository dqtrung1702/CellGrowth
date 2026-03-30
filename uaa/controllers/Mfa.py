from flask import Blueprint, request

from utils.http import json_response, validate_body
from utils.token import current_user_id
from schemas.response import ResponseEnvelope
from schemas.mfa import EnrollTOTPRequest, VerifyTOTPRequest, DisableTOTPRequest
from services.container import totp_service

mfa_bp = Blueprint("mfa", __name__)
_totp = totp_service()


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
    # same logic as verify_totp, used in login flow
    return verify_totp()


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
