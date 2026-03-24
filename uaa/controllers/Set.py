"""
Endpoints:
- POST   /getSetList
- POST   /addSet
- POST   /updateSet
- POST   /deleteSetById
- POST   /getDatasetBySet
- POST   /updateDatasetBySet
"""

from flask import Blueprint, request

from utils.http import json_response, validate_body
from utils.token import current_user_id
from services.container import set_service
from schemas.set import (
    SetListRequest,
    AddSetRequest,
    UpdateSetRequest,
    DeleteSetRequest,
    DatasetBySetRequest,
    UpdateDatasetBySetRequest,
)

set_bp = Blueprint("set_api", __name__)
_set_service = set_service()


@set_bp.route("/getSetList", methods=["POST"])
@validate_body(SetListRequest)
def get_set_list():
    payload: SetListRequest = request.parsed_obj
    setname = payload.SetName
    services = payload.Services
    setcode = payload.SetCode

    requester_id = current_user_id()
    resp = _set_service.list_sets(requester_id, setname, services, setcode)
    return json_response(resp)


@set_bp.route("/addSet", methods=["POST"])
@validate_body(AddSetRequest)
def add_set():
    payload: AddSetRequest = request.parsed_obj
    payload_dict = payload.model_dump()
    resp = _set_service.add_set({"SetName": payload_dict["SetName"], "Services": payload_dict["Services"], "SetCode": payload_dict["SetCode"]})
    return json_response(resp, status=200 if resp.status == "OK" else 400)


@set_bp.route("/updateSet", methods=["POST"])
@validate_body(UpdateSetRequest)
def update_set():
    payload: UpdateSetRequest = request.parsed_obj
    set_id = payload.SetId
    tmp_payload = {"SetName": payload.SetName, "Services": payload.Services, "SetCode": payload.SetCode}
    resp = _set_service.update_set(set_id, tmp_payload)
    status = 200 if resp.status == "OK" else (409 if resp.message and "trùng" in resp.message else 400)
    return json_response(resp, status=status)


@set_bp.route("/deleteSetById", methods=["POST"])
@validate_body(DeleteSetRequest)
def delete_set_by_id():
    payload: DeleteSetRequest = request.parsed_obj
    sid = payload.SetId or payload.id

    resp = _set_service.delete_set(sid)
    return json_response(resp)


@set_bp.route("/getDatasetBySet", methods=["POST"])
@validate_body(DatasetBySetRequest)
def get_dataset_by_set():
    payload: DatasetBySetRequest = request.parsed_obj
    sid = payload.SetId

    requester_id = current_user_id()
    resp = _set_service.dataset_by_set(requester_id, sid)
    return json_response(resp, status=200 if resp.status == "OK" else 403)


@set_bp.route("/updateDatasetBySet", methods=["POST"])
@validate_body(UpdateDatasetBySetRequest)
def update_dataset_by_set():
    payload: UpdateDatasetBySetRequest = request.parsed_obj
    sid = payload.SetId
    items = payload.Data or []

    resp = _set_service.update_dataset_by_set(sid, items)
    return json_response(resp, status=200 if resp.status == "OK" else 400)


__all__ = [
    "set_bp",
]
