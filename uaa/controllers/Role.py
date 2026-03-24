"""
Endpoints:
- POST   /getRoleList
- GET    /publicRoleList
- POST   /getRoleInfo
- POST   /addRole
- POST   /updateRole
- POST   /deleteRoleById
- POST   /getPermissionByRole
- POST   /getUserByRole
- POST   /getRoleByUser
- POST   /getRolePermissionList
- POST   /getRoleByPermission
"""

from flask import Blueprint, request

from utils.http import json_response, validate_body
from utils.token import current_user_id
from services.container import role_service
from schemas.role import (
    RoleListRequest,
    RoleInfoRequest,
    AddRoleRequest,
    UpdateRoleRequest,
    DeleteRoleRequest,
    PermissionByRoleRequest,
    UserByRoleRequest,
    RoleByUserRequest,
    RolePermissionListRequest,
    RoleByPermissionRequest,
)

role_bp = Blueprint("role_api", __name__)
_role_service = role_service()


@role_bp.route("/getRoleList", methods=["POST"])
@validate_body(RoleListRequest)
def get_role_list():
    payload: RoleListRequest = request.parsed_obj
    page = int(payload.page)
    page_size = int(payload.page_size)
    code = payload.Code
    requester_id = current_user_id()
    resp = _role_service.list_roles(requester_id, page, page_size, code)
    return json_response(resp)


@role_bp.route("/publicRoleList", methods=["GET"])
def public_role_list():
    page = int(request.args.get("page", 1))
    page_size = min(int(request.args.get("page_size", 50)), 200)
    code = request.args.get("code")
    resp = _role_service.public_roles(page, page_size, code)
    return json_response(resp)


@role_bp.route("/getRoleInfo", methods=["POST"])
@validate_body(RoleInfoRequest)
def get_role_info():
    payload: RoleInfoRequest = request.parsed_obj
    role_id = payload.id

    requester_id = current_user_id()
    resp = _role_service.get_role_info(requester_id, role_id)
    return json_response(resp, status=200 if resp.status == "OK" else 404)


@role_bp.route("/addRole", methods=["POST"])
@validate_body(AddRoleRequest)
def add_role():
    payload: AddRoleRequest = request.parsed_obj
    code = payload.Code
    description = payload.Description
    perm_ids = [int(pid) for pid in payload.Permission]
    resp = _role_service.add_role(code, description, perm_ids)
    return json_response(resp, status=200 if resp.status == "OK" else 500)


@role_bp.route("/updateRole", methods=["POST"])
@validate_body(UpdateRoleRequest)
def update_role():
    payload: UpdateRoleRequest = request.parsed_obj
    rid = payload.RoleId
    description = payload.Description
    perm_ids = [int(pid) for pid in payload.Permission]

    resp = _role_service.update_role(rid, description, perm_ids)
    return json_response(resp, status=200 if resp.status == "OK" else 500)


@role_bp.route("/deleteRoleById", methods=["POST"])
@validate_body(DeleteRoleRequest)
def delete_role():
    payload: DeleteRoleRequest = request.parsed_obj
    rid = payload.id

    resp = _role_service.delete_role(rid)
    return json_response(resp)


@role_bp.route("/getPermissionByRole", methods=["POST"])
@validate_body(PermissionByRoleRequest)
def get_permission_by_role():
    payload: PermissionByRoleRequest = request.parsed_obj
    resp = _role_service.permissions_of_role(payload.id)
    return json_response(resp)


@role_bp.route("/getUserByRole", methods=["POST"])
@validate_body(UserByRoleRequest)
def get_user_by_role():
    payload: UserByRoleRequest = request.parsed_obj
    resp = _role_service.users_of_role(payload.id)
    return json_response(resp)


@role_bp.route("/getRoleByUser", methods=["POST"])
@validate_body(RoleByUserRequest)
def get_role_by_user():
    payload: RoleByUserRequest = request.parsed_obj
    uid = payload.id or payload.UserId

    resp = _role_service.roles_of_user(uid)
    return json_response(resp)


@role_bp.route("/getRolePermissionList", methods=["POST"])
@validate_body(RolePermissionListRequest)
def get_role_permission_list():
    payload: RolePermissionListRequest = request.parsed_obj
    page = int(payload.page)
    page_size = int(payload.page_size)
    code = payload.Code
    ptype = payload.PermissionType or payload.PermissionTypes
    resp = _role_service.role_permission_list(page, page_size, code, ptype)
    return json_response(resp)


@role_bp.route("/getRoleByPermission", methods=["POST"])
@validate_body(RoleByPermissionRequest)
def get_role_by_permission():
    payload: RoleByPermissionRequest = request.parsed_obj
    resp = _role_service.roles_by_permission(payload.id)
    return json_response(resp)


__all__ = ["role_bp"]
