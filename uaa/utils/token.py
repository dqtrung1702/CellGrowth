from typing import Optional
from flask import request
import jwt

from config import Config


def extract_token():
    token = request.cookies.get("app_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    return token


def current_user_id() -> Optional[int]:
    token = extract_token()
    if not token:
        return None
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload.get("UserId")
    except Exception:
        return None
