from typing import List, Optional, Tuple
import json
from datetime import datetime

from repositories.access_request_repository import AccessRequestRepository
from repositories.user_repository import UserRepository
from repositories.interfaces import AccessRequestRepoProtocol, UserRepoProtocol
from services.access_request_apply_service import AccessRequestApplyService


class AccessRequestApprovalService:
    """Xử lý approve/reject/cancel tách khỏi CRUD/list."""

    def __init__(
        self,
        ar_repo: Optional[AccessRequestRepoProtocol] = None,
        user_repo: Optional[UserRepoProtocol] = None,
        apply_service: Optional[AccessRequestApplyService] = None,
    ):
        self.ar_repo: AccessRequestRepoProtocol = ar_repo or AccessRequestRepository()
        self.user_repo: UserRepoProtocol = user_repo or UserRepository()
        self.apply_service = apply_service or AccessRequestApplyService()

    def _apply_items(self, items: List[dict], target_user: int) -> List[dict]:
        return self.apply_service.apply_items(items, target_user, self.user_repo)

    def approve(self, req_id: int, approver_id: int, note: Optional[str] = None) -> Tuple[Optional[dict], Optional[List[dict]], Optional[List[dict]]]:
        res = self.ar_repo.get_request_with_items(req_id)
        if not res or res[0] is None:
            return None, None, None
        req_row, items, _ = res
        if req_row.get("status") != "SUBMITTED":
            return req_row, None, None
        actions = self._apply_items(items, req_row["requester_id"])
        self.ar_repo.approve_request(req_id, approver_id, actions, note)
        return req_row, items, actions

    def reject(self, req_id: int, actor_id: int, note: str):
        return self.ar_repo.reject_request(req_id, actor_id, note)

    def cancel(self, req_id: int, actor_id: int):
        return self.ar_repo.cancel_request(req_id, actor_id)
