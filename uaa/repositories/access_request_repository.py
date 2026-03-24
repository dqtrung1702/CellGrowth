from datetime import datetime
from typing import List, Optional
import json

from sqlalchemy import text

from .orm_base import OrmRepo
from models.entities import AccessRequest, AccessRequestItem, AccessRequestLog, User, Role, Permission


class AccessRequestRepository(OrmRepo):
    def create_request(self, requester_id: int, requester_username: str, request_type: str, reason: str, ttl_hours: Optional[int]):
        with self.session() as session:
            obj = AccessRequest(
                requester_id=requester_id,
                requester=requester_username,
                request_type=request_type,
                status="SUBMITTED",
                reason=reason,
                ttl_hours=ttl_hours,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(obj)
            session.flush()
            return obj.id

    def add_items(self, req_id: int, items: List[dict]):
        with self.session() as session:
            for it in items:
                session.add(
                    AccessRequestItem(
                        request_id=req_id,
                        role_id=it.get("role_id"),
                        data_permission_id=it.get("data_permission_id"),
                        note=it.get("note"),
                        created_at=datetime.utcnow(),
                    )
                )

    def add_log(self, session, request_id: int, actor_id: int, action: str, note: Optional[str] = None):
        session.add(
            AccessRequestLog(
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                note=note,
                created_at=datetime.utcnow(),
            )
        )

    def log_action(self, request_id: int, actor_id: int, action: str, note: Optional[str] = None):
        with self.session() as session:
            self.add_log(session, request_id, actor_id, action, note=note)

    def replace_items(self, req_id: int, items: List[dict]):
        with self.session() as session:
            session.query(AccessRequestItem).filter(AccessRequestItem.request_id == req_id).delete(synchronize_session=False)
            for it in items:
                session.add(
                    AccessRequestItem(
                        request_id=req_id,
                        role_id=it.get("role_id"),
                        data_permission_id=it.get("data_permission_id"),
                        note=it.get("note"),
                        created_at=datetime.utcnow(),
                    )
                )

    def get_request_with_items(self, req_id: int):
        with self.session() as session:
            req_row = (
                session.query(
                    AccessRequest,
                    User.username.label("requester_username"),
                )
                .outerjoin(User, User.id == AccessRequest.requester_id)
                .filter(AccessRequest.id == req_id)
                .first()
            )
            if not req_row:
                return None, None, None
            req_obj = req_row.AccessRequest
            items = (
                session.query(
                    AccessRequestItem.id,
                    AccessRequestItem.role_id,
                    Role.code.label("role_code"),
                    AccessRequestItem.data_permission_id,
                    Permission.code.label("data_permission_code"),
                    AccessRequestItem.note,
                )
                .outerjoin(Role, Role.id == AccessRequestItem.role_id)
                .outerjoin(Permission, Permission.id == AccessRequestItem.data_permission_id)
                .filter(AccessRequestItem.request_id == req_id)
                .order_by(AccessRequestItem.id)
                .all()
            )
            logs = (
                session.query(
                    AccessRequestLog.id,
                    AccessRequestLog.actor_id,
                    User.username.label("actor_username"),
                    AccessRequestLog.action,
                    AccessRequestLog.note,
                    AccessRequestLog.created_at,
                )
                .outerjoin(User, User.id == AccessRequestLog.actor_id)
                .filter(AccessRequestLog.request_id == req_id)
                .order_by(AccessRequestLog.created_at.asc())
                .all()
            )
            return dict(requester_username=req_row.requester_username, **req_obj.__dict__), [dict(r._mapping) for r in items], [dict(r._mapping) for r in logs]

    def approve_request(self, req_id: int, approver_id: int, actions: List[dict], note: Optional[str]):
        with self.session() as session:
            req_obj = session.get(AccessRequest, req_id, with_for_update=True)
            if not req_obj:
                return None
            if req_obj.status != "SUBMITTED":
                return req_obj
            items = (
                session.query(AccessRequestItem)
                .filter(AccessRequestItem.request_id == req_id)
                .all()
            )
            req_obj.status = "APPROVED"
            req_obj.approved_by = approver_id
            req_obj.approved_at = datetime.utcnow()
            req_obj.updated_at = datetime.utcnow()
            req_obj.apply_result_json = json.dumps(actions)
            self.add_log(session, req_id, approver_id, "APPROVE", note=note)
            return req_obj.__dict__, [i.__dict__ for i in items]

    def reject_request(self, req_id: int, actor_id: int, note: str):
        with self.session() as session:
            req_obj = session.get(AccessRequest, req_id, with_for_update=True)
            if not req_obj:
                return None
            if req_obj.status != "SUBMITTED":
                return req_obj
            req_obj.status = "REJECTED"
            req_obj.rejected_reason = note
            req_obj.updated_at = datetime.utcnow()
            self.add_log(session, req_id, actor_id, "REJECT", note=note)
            return req_obj.__dict__

    def cancel_request(self, req_id: int, actor_id: int):
        with self.session() as session:
            req_obj = session.get(AccessRequest, req_id, with_for_update=True)
            if not req_obj:
                return None
            if req_obj.requester_id != actor_id:
                return "FORBIDDEN"
            if req_obj.status != "SUBMITTED":
                return req_obj
            req_obj.status = "CANCELLED"
            req_obj.updated_at = datetime.utcnow()
            self.add_log(session, req_id, actor_id, "CANCEL")
            return req_obj.__dict__
