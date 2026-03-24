from typing import List

from repositories.interfaces import UserRepoProtocol


class AccessRequestApplyService:
    """Tách logic áp dụng AccessRequest để thu hẹp AccessRequestService."""

    def apply_items(self, items: List[dict], target_user: int, user_repo: UserRepoProtocol) -> List[dict]:
        actions: List[dict] = []
        role_ids = [it.get("role_id") for it in items if it.get("role_id")]
        if role_ids:
            user_repo.add_roles(target_user, role_ids)
            actions.extend({"role_id": rid, "action": "added"} for rid in role_ids)

        data_perm_ids = [it.get("data_permission_id") for it in items if it.get("data_permission_id")]
        if data_perm_ids:
            user_repo.set_data_permission(target_user, data_perm_ids[0])
            actions.append({"data_permission_id": data_perm_ids[0], "action": "set"})

        return actions
