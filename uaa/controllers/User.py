"""
Endpoints:
- POST   /getUserList
- POST   /getUserInfo
- POST   /updateUser
- POST   /updateUserRole
"""

from flask import Blueprint, request

from utils.http import json_response, validate_body
from utils.token import current_user_id
from services.container import user_service
from schemas.response import ResponseEnvelope, PaginationMeta
from schemas.user import (
    UserListRequest,
    UserInfoRequest,
    UpdateUserRequest,
    UpdateUserRoleRequest,
)

user_bp = Blueprint("user_api", __name__)
_user_service = user_service()


@user_bp.route("/getUserList", methods=["POST"])
@validate_body(UserListRequest)
def get_user_list():
    payload: UserListRequest = request.parsed_obj
    page = int(payload.page)
    page_size = int(payload.page_size)
    username_filter = payload.UserName
    requester_id = current_user_id()
    resp = _user_service.list_users(requester_id, page, page_size, username_filter)
    return json_response(resp, status=200)


@user_bp.route("/getUserInfo", methods=["POST"])
@validate_body(UserInfoRequest)
def get_user_info():
    payload: UserInfoRequest = request.parsed_obj
    user_id = payload.id
    requester_id = current_user_id()
    resp = _user_service.get_user_info(requester_id, user_id)
    return json_response(resp, status=200 if resp.status == "OK" else 404)


@user_bp.route("/updateUser", methods=["POST"])
@validate_body(UpdateUserRequest)
def update_user():
    payload: UpdateUserRequest = request.parsed_obj
    user_id = payload.id
    resp = _user_service.update_user(
        user_id,
        payload.UserLocked,
        payload.Password,
        payload.NameDisplay,
        payload.DataPermission,
    )
    return json_response(resp, status=200 if resp.status == "OK" else 400)


@user_bp.route("/updateUserRole", methods=["POST"])
@validate_body(UpdateUserRoleRequest)
def update_user_role():
    payload: UpdateUserRoleRequest = request.parsed_obj
    user_id = payload.UserId
    role_list = payload.RoleList or []
    resp = _user_service.update_user_role(user_id, role_list)
    return json_response(resp, status=200)


__all__ = ["user_bp"]
