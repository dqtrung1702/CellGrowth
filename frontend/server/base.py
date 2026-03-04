from functools import wraps
import secrets

from flask import request, redirect, session, abort
from config import Config
import jwt


def _menu_flags_from_session():
    """Normalize menu flag storage into a dict of {MenuId: bool}."""
    raw = session.get("MenuFlags") or session.get("MenuList")
    print("Raw menu flags:", raw)
    if isinstance(raw, dict):
        return {str(k): bool(v) for k, v in raw.items()}
    flags = {}
    for item in raw or []:
        flags[str(item)] = True
    return flags


def inject_menu_flags():
    """Context processor to expose menu flags to all templates."""
    return {"menu_flags": _menu_flags_from_session()}


def auth(jwt_token):
    try:
        auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
        return bool(auth_info)
    except Exception:
        return False


def auth_info(jwt_token):
    try:
        auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
        if auth_info:
            return True, auth_info
    except Exception:
        pass
    return False, None


def require_page_access(view_func):
    """
    Decorator: chỉ kiểm tra đăng nhập bằng JWT; phân quyền trang chi tiết đã gỡ bỏ.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        jwt_token = request.cookies.get("app_token", "")
        if not auth(jwt_token):
            return redirect("Accessisdenied")
        return view_func(*args, **kwargs)

    return wrapper


def issue_csrf_token():
    """Create/reuse CSRF token stored in session."""
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["csrf_token"] = token
    return token


def _extract_csrf():
    """Read CSRF token from header or form/json fields."""
    header = request.headers.get("X-CSRFToken")
    if header:
        return header
    if request.form:
        return request.form.get("_csrf")
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return data.get("_csrf")
    return None


def csrf_protect():
    """Global CSRF guard for unsafe HTTP methods."""
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        # allow auth endpoints without CSRF (login/register) so user có thể lấy token lần đầu
        if request.endpoint in ("auth_blueprint.login", "auth_blueprint.register"):
            return
        expected = session.get("csrf_token")
        received = _extract_csrf()
        if not expected or not received or expected != received:
            abort(403)


def attach_csrf_cookie(response):
    """Set CSRF token cookie for client-side JS/form; not HttpOnly to allow JS header."""
    token = issue_csrf_token()
    response.set_cookie("csrf_token", token, path="/", httponly=False, samesite="Lax")
    return response
