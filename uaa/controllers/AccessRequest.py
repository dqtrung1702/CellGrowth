"""
Endpoints:
- POST   /access_requests
- GET    /access_requests
- GET    /access_requests/<id>
- POST   /access_requests/<id>/approve
- POST   /access_requests/<id>/reject
- POST   /access_requests/<id>/cancel
"""

from flask import Blueprint, request

from utils.http import json_response, validate_body
from utils.token import current_user_id
from utils.data_scope import data_scope_filters
from utils.idempotency import idempotency, ensure_request_id
from utils.audit import audit_log
from schemas.response import ResponseEnvelope
from schemas.access_request import (
    AccessRequestCreate,
    AccessRequestApprove,
    AccessRequestReject,
    AccessRequestListQuery,
)
from services.container import access_request_service, access_request_approval_service
from models.orm import SessionLocal

ar_bp = Blueprint("access_request_api", __name__)
_ar_service = access_request_service()
_ar_approval_service = access_request_approval_service()
_session_factory = getattr(_ar_service.ar_repo, "_session_factory", SessionLocal)


def _check_scope_for_request(req_id, scope_sql, scope_params):
    if not scope_sql:
        return True
    from sqlalchemy import text

    from repositories.orm_base import OrmRepo

    binder = OrmRepo(_session_factory)
    sql, bind = binder._bind_sql(f"SELECT 1 FROM access_requests WHERE id=%s AND {scope_sql};", [req_id] + (scope_params or []))
    with binder.session() as session:
        return bool(session.execute(text(sql), bind).first())


@ar_bp.route("/access_requests", methods=["POST"])
@validate_body(AccessRequestCreate)
def create_request():
    rid = ensure_request_id()
    payload: AccessRequestCreate = request.parsed_obj
    user_id = current_user_id()
    if not user_id:
        audit_log("access_request.create", None, "FAIL", {"reason": "unauthorized"}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    req_type = (payload.Type or "ROLE").upper()
    if req_type not in ("ROLE", "DATA"):
        return json_response({"message": "Type must be ROLE or DATA", "status": "FAIL"}, status=400)

    roles = payload.Roles or []
    data_perms = payload.DataPermissions or []
    if not roles and not data_perms:
        return json_response({"message": "At least one role or data scope is required", "status": "FAIL"}, status=400)

    requester_username = _ar_service.user_repo.get_username(user_id)
    req_id = _ar_service.create(user_id, requester_username, req_type, payload.Reason, payload.TtlHours, roles, data_perms)

    audit_log("access_request.create", user_id, "OK", {"request_id": req_id}, request_id=rid, path=request.path)
    return json_response(ResponseEnvelope(status="OK", data={"RequestId": req_id}), status=200)

@ar_bp.route("/access_requests/<int:req_id>/update", methods=["POST"])
@validate_body(AccessRequestCreate)
@idempotency()
def update_request(req_id):
    rid = ensure_request_id()
    user_id = current_user_id()
    if not user_id:
        audit_log("access_request.update", None, "FAIL", {"reason": "unauthorized", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    payload: AccessRequestCreate = request.parsed_obj
    if payload.Type and payload.Type.upper() not in ("ROLE", "DATA"):
        return json_response(ResponseEnvelope(status="FAIL", message="Type must be ROLE or DATA"), status=400)

    roles = payload.Roles if payload.Roles else None
    data_perms = payload.DataPermissions if payload.DataPermissions else None

    result = _ar_service.update(req_id, user_id, roles, data_perms, payload.Reason)
    if result is None:
        return json_response(ResponseEnvelope(status="FAIL", message="Not found"), status=404)
    if result == "FORBIDDEN":
        return json_response(ResponseEnvelope(status="FAIL", message="Forbidden"), status=403)
    if isinstance(result, dict) and result.get("status") and result.get("status") != "SUBMITTED":
        return json_response(ResponseEnvelope(status="FAIL", message="Request not in SUBMITTED"), status=400)

    audit_log("access_request.update", user_id, "OK", {"request_id": req_id}, request_id=rid, path=request.path)
    return json_response(ResponseEnvelope(status="OK"))


@ar_bp.route("/access_requests", methods=["GET"])
def list_requests():
    ensure_request_id()
    user_id = current_user_id()
    if not user_id:
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    payload = AccessRequestListQuery(**request.args)
    resp = _ar_service.list(user_id, payload)
    return json_response(resp)


@ar_bp.route("/access_requests/<int:req_id>", methods=["GET"])
def get_request(req_id):
    rid = ensure_request_id()
    user_id = current_user_id()
    if not user_id:
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    req_row, items, logs = _ar_service.get(req_id)
    if not req_row:
        return json_response(ResponseEnvelope(status="FAIL", message="Not found"), status=404)

    if req_row.get("requester_id") != user_id:
        scope_sql, scope_params = data_scope_filters(_session_factory, user_id, table_name="access_requests")
        if scope_sql and not _check_scope_for_request(req_id, scope_sql, scope_params):
            return json_response(ResponseEnvelope(status="FAIL", message="Access denied"), status=403)

    req_row["Items"] = items or []
    req_row["Logs"] = logs or []
    return json_response(ResponseEnvelope(status="OK", data=req_row))


@ar_bp.route("/access_requests/<int:req_id>/approve", methods=["POST"])
@validate_body(AccessRequestApprove)
@idempotency()
def approve_request(req_id):
    rid = ensure_request_id()
    user_id = current_user_id()
    if not user_id:
        audit_log("access_request.approve", None, "FAIL", {"reason": "unauthorized", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    payload: AccessRequestApprove = request.parsed_obj
    req_row, items, actions = _ar_approval_service.approve(req_id, user_id, note=payload.Note)
    if req_row is None:
        audit_log("access_request.approve", user_id, "FAIL", {"reason": "not_found", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Not found"), status=404)
    if items is None:
        audit_log("access_request.approve", user_id, "FAIL", {"reason": "not_submitted", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Request not in SUBMITTED"), status=400)

    audit_log("access_request.approve", user_id, "OK", {"request_id": req_id, "actions": actions}, request_id=rid, path=request.path)
    return json_response(ResponseEnvelope(status="OK", data={"actions": actions or []}))


@ar_bp.route("/access_requests/<int:req_id>/reject", methods=["POST"])
@validate_body(AccessRequestReject)
@idempotency()
def reject_request(req_id):
    rid = ensure_request_id()
    user_id = current_user_id()
    if not user_id:
        audit_log("access_request.reject", None, "FAIL", {"reason": "unauthorized", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    payload: AccessRequestReject = request.parsed_obj
    note = payload.Note or payload.Reason
    if not note:
        return json_response(ResponseEnvelope(status="FAIL", message="Reject note is required"), status=400)

    result = _ar_approval_service.reject(req_id, user_id, note)
    if result is None:
        audit_log("access_request.reject", user_id, "FAIL", {"reason": "not_found", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Not found"), status=404)
    if isinstance(result, dict) and result.get("status") and result.get("status") != "SUBMITTED":
        audit_log("access_request.reject", user_id, "FAIL", {"reason": "not_submitted", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Request not in SUBMITTED"), status=400)

    audit_log("access_request.reject", user_id, "OK", {"request_id": req_id}, request_id=rid, path=request.path)
    return json_response(ResponseEnvelope(status="OK"))


@ar_bp.route("/access_requests/<int:req_id>/cancel", methods=["POST"])
@idempotency()
def cancel_request(req_id):
    rid = ensure_request_id()
    user_id = current_user_id()
    if not user_id:
        audit_log("access_request.cancel", None, "FAIL", {"reason": "unauthorized", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Unauthorized"), status=401)

    result = _ar_approval_service.cancel(req_id, user_id)
    if result is None:
        audit_log("access_request.cancel", user_id, "FAIL", {"reason": "not_found", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Not found"), status=404)
    if result == "FORBIDDEN":
        audit_log("access_request.cancel", user_id, "FAIL", {"reason": "forbidden", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Forbidden"), status=403)
    if isinstance(result, dict) and result.get("status") and result.get("status") != "SUBMITTED":
        audit_log("access_request.cancel", user_id, "FAIL", {"reason": "not_submitted", "request_id": req_id}, request_id=rid, path=request.path)
        return json_response(ResponseEnvelope(status="FAIL", message="Request not in SUBMITTED"), status=400)

    audit_log("access_request.cancel", user_id, "OK", {"request_id": req_id}, request_id=rid, path=request.path)
    return json_response(ResponseEnvelope(status="OK"))


__all__ = ["ar_bp"]
