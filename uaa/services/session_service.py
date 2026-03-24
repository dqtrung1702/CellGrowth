from typing import Optional, Tuple

from flask import session


def set_user_session(user_id: Optional[int], username: str) -> None:
    """Persist authenticated user info into server-side session."""
    session["UserId"] = user_id
    session["UserName"] = username


def clear_user_session() -> None:
    session.pop("UserId", None)
    session.pop("UserName", None)


def get_user_session() -> Tuple[Optional[int], str]:
    """Return (UserId, UserName) from session; missing values become (None, '')."""
    return session.get("UserId"), session.get("UserName", "")


def is_session_user(user_id: Optional[int]) -> bool:
    """Check whether current session belongs to given user id."""
    return session.get("UserId") == user_id
