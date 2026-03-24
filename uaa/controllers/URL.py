"""
Endpoints:
- POST   /getURLbyPermission
- POST   /getURLbyPermissionList
- POST   /getPageByUser
"""

from flask import Blueprint, request

from utils.http import json_response, validate_body
from services.container import url_page_service
from schemas.url import (
    URLByPermissionRequest,
    URLByPermissionListRequest,
    PageByUserRequest,
)

url_bp = Blueprint("url_api", __name__)
_url_service = url_page_service()  # UrlPageService tách khỏi DataService


@url_bp.route("/getURLbyPermission", methods=["POST"])
@validate_body(URLByPermissionRequest)
def get_url_by_permission():
    payload: URLByPermissionRequest = request.parsed_obj
    resp = _url_service.urls_by_permission(payload.PermissionId)
    return json_response(resp)


@url_bp.route("/getURLbyPermissionList", methods=["POST"])
@validate_body(URLByPermissionListRequest)
def get_url_by_permission_list():
    """Nhận PermissionList (id hoặc code), trả về danh sách url/method/type."""
    payload: URLByPermissionListRequest = request.parsed_obj
    perms = payload.PermissionList or []

    resp = _url_service.urls_by_permission_list(perms)
    return json_response(resp)


@url_bp.route("/getPageByUser", methods=["POST"])
@validate_body(PageByUserRequest)
def get_page_by_user():
    """Return distinct pages a user can access based on roles -> permissions -> page_permissions."""
    payload: PageByUserRequest = request.parsed_obj
    resp = _url_service.pages_by_user(payload.UserId)
    return json_response(resp)


__all__ = ["url_bp"]
