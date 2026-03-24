import json
import os
from datetime import datetime
from typing import Optional

from config import Config


def audit_log(action: str, user_id: Optional[int], status: str, detail: Optional[dict] = None, request_id: Optional[str] = None, path: Optional[str] = None):
    """
    Ghi log audit JSONL: một dòng cho mỗi sự kiện.
    Fields: ts, action, user_id, status, path, request_id, detail
    """
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "user_id": user_id,
        "status": status,
        "path": path,
        "request_id": request_id,
        "detail": detail or {},
    }
    log_path = Config.AUDIT_LOG_PATH
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        # best effort, không raise
        pass
