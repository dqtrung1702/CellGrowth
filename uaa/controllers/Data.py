"""
Endpoints:
- POST   /getDataSetByUser
- POST   /getDatasetByPermission
- POST   /getPermissionInfo
- POST   /addPermission
- POST   /updatePermission
- POST   /deletePermissionById
- POST   /getPermissionList
- POST   /getDataPermissionList
- GET    /publicPermissionList
"""

from flask import Blueprint, request
from utils.http import json_response, validate_body
from utils.token import current_user_id
from services.container import data_service, permission_service
from schemas.data import (
    DataSetByUserRequest,
    DatasetByPermissionRequest,
    PermissionInfoRequest,
    AddPermissionRequest,
    UpdatePermissionRequest,
    DeletePermissionRequest,
    PermissionListRequest,
    DataPermissionListRequest,
)

data_bp = Blueprint("data_api", __name__)
_data_service = data_service()
_permission_service = permission_service()


@data_bp.route("/getDataSetByUser", methods=["POST"])
@validate_body(DataSetByUserRequest)
def get_dataset_by_user():
    payload: DataSetByUserRequest = request.parsed_obj
    resp = _data_service.dataset_by_user(payload.UserId)
    return json_response(resp)


@data_bp.route("/getDatasetByPermission", methods=["POST"])
@validate_body(DatasetByPermissionRequest)
def get_dataset_by_permission():
    payload: DatasetByPermissionRequest = request.parsed_obj
    resp = _data_service.dataset_by_permission(payload.PermissionId)
    return json_response(resp)


@data_bp.route("/getPermissionInfo", methods=["POST"])
@validate_body(PermissionInfoRequest)
def get_permission_info():
    payload: PermissionInfoRequest = request.parsed_obj
    ids_int = [int(i) for i in payload.ids] if payload.ids else []
    requester_id = current_user_id()
    resp = _permission_service.permission_info(requester_id, ids_int)
    return json_response(resp)


@data_bp.route("/addPermission", methods=["POST"])
@validate_body(AddPermissionRequest)
def add_permission():
    payload: AddPermissionRequest = request.parsed_obj
    code = payload.Code
    ptype_raw = (payload.PermissionType or "ROLE").upper()
    ptype = "DATA" if ptype_raw == "DATA" else "ROLE"
    description = payload.Description
    url_list = payload.UrlList or []
    data_sets = payload.DataSets or []

    resp = _permission_service.add_permission(code, ptype, description, url_list, data_sets)
    status = 200 if resp.status == "OK" else (409 if resp.message == "Permission code already exists" else 400)
    return json_response(resp, status=status)


@data_bp.route("/updatePermission", methods=["POST"])
@validate_body(UpdatePermissionRequest)
def update_permission():
    payload: UpdatePermissionRequest = request.parsed_obj
    pid = payload.PermissionId

    description = payload.Description
    ptype_raw = payload.PermissionType
    if ptype_raw is not None:
        ptype_raw = str(ptype_raw).upper()
    ptype = "DATA" if ptype_raw == "DATA" else ("ROLE" if ptype_raw else None)
    url_list = payload.UrlList or []
    data_sets = payload.DataSets or []

    if ptype is None:
        # tránh hit DB thêm, reuse service to fetch type
        from repositories.permission_repository import PermissionRepository
        ptype = "DATA" if str(PermissionRepository().get_permission_type(pid) or "ROLE").upper() == "DATA" else "ROLE"
    resp = _permission_service.update_permission(pid, description, ptype, url_list, data_sets)
    return json_response(resp, status=200 if resp.status == "OK" else 400)


@data_bp.route("/deletePermissionById", methods=["POST"])
@validate_body(DeletePermissionRequest)
def delete_permission():
    payload: DeletePermissionRequest = request.parsed_obj
    resp = _permission_service.delete_permission(payload.id)
    return json_response(resp)


@data_bp.route("/getPermissionList", methods=["POST"])
@validate_body(PermissionListRequest)
def get_permission_list():
    payload: PermissionListRequest = request.parsed_obj
    page = int(payload.page)
    page_size = int(payload.page_size)
    code = payload.Code
    ptype_raw = payload.PermissionType
    ptype_list = None
    if isinstance(ptype_raw, (list, tuple, set)):
        ptype_list = [str(p).upper() for p in ptype_raw]
    elif ptype_raw:
        p = str(ptype_raw).upper()
        ptype_list = [p] if p else None

    requester_id = current_user_id()
    resp = _permission_service.list_permissions(requester_id, page, page_size, code, ptype_list)
    return json_response(resp)


@data_bp.route("/getDataPermissionList", methods=["POST"])
@validate_body(DataPermissionListRequest)
def get_data_permission_list():
    payload: DataPermissionListRequest = request.parsed_obj
    page = int(payload.page)
    page_size = int(payload.page_size)
    code = payload.Code
    resp = _permission_service.list_data_permissions(page, page_size, code)
    return json_response(resp)


@data_bp.route("/publicPermissionList", methods=["GET"])
def public_permission_list():
    page = int(request.args.get("page", 1))
    page_size = min(int(request.args.get("page_size", 50)), 200)
    code = request.args.get("code")
    resp = _permission_service.public_data_permissions(page, page_size, code)
    return json_response(resp)


__all__ = ["data_bp"]
