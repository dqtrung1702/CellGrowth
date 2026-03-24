from services.access_request_service import AccessRequestService


class FakeARRepo:
    def __init__(self):
        self.created = None
        self.items = None
        self.logs = []

    def create_request(self, requester_id, requester_username, request_type, reason, ttl_hours):
        self.created = (requester_id, requester_username, request_type, reason, ttl_hours)
        return 5

    def add_items(self, req_id, items):
        self.items = (req_id, items)

    def log_action(self, req_id, actor_id, action, note=None):
        self.logs.append((req_id, actor_id, action, note))

    def conn(self):
        raise RuntimeError("conn should not be used in create() test")


class FakeUserRepo:
    def add_roles(self, user_id, role_ids):
        self.added_roles = (user_id, role_ids)

    def set_data_permission(self, user_id, perm_id):
        self.set_dp = (user_id, perm_id)

    def get_username(self, user_id):
        return "user"


def test_create_request_writes_items_and_log():
    ar_repo = FakeARRepo()
    user_repo = FakeUserRepo()
    svc = AccessRequestService(ar_repo=ar_repo, user_repo=user_repo)
    req_id = svc.create(1, "tester", "ROLE", "why", 2, [10], [20], [30])
    assert req_id == 5
    assert ar_repo.created == (1, "tester", "ROLE", "why", 2)
    assert ar_repo.items[0] == 5
    # ensure three item types recorded
    assert len(ar_repo.items[1]) == 3
    assert ar_repo.logs[0][2] == "SUBMIT"
