from functools import wraps
import secrets

from flask import request, redirect, session, abort
from config import Config
import jwt
import requests

PAGE_MENU_MAP = {
    "home": "Home",
    "role": "Roles",
    "permission": "Permissions",
    "user": "Users",
    "datasets": "DataSets",
    "access_requests": "AccessRequests",
    "mfa/totp/setup": "TOTP",
}

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


def _build_menu_flags(page_items):
    # Home luôn hiển thị; AccessRequests hiển thị mặc định để user có thể gửi/xem yêu cầu của chính mình
    flags = {"Home": True, "AccessRequests": True}
    for item in page_items or []:
        page = (item or {}).get("Page") or (item or {}).get("page") or ""
        norm = page.strip().strip("/").lower()
        menu_id = PAGE_MENU_MAP.get(norm)
        if menu_id:
            flags[menu_id] = True
    return flags


def _ensure_menu_flags(cookies, user_id: int):
    flags = _menu_flags_from_session()
    if flags:
        return flags
    # fetch from UAA if missing
    try:
        res = requests.post(Config.UAA_URL + "/getPageByUser", json={"UserId": user_id}, cookies=cookies, timeout=5)
        if res.status_code == 200 and (res.json() or {}).get("status") == "OK":
            pages = res.json().get("data", [])
            flags = _build_menu_flags(pages)
            session["MenuFlags"] = flags
            return flags
    except Exception:
        pass
    return flags or {}


def _path_to_menu_id(path: str):
    norm = (path or "").strip().strip("/").lower()
    if not norm:
        return "Home"
    if norm.startswith("role"):
        return PAGE_MENU_MAP.get("role")
    if norm.startswith("permission"):
        return PAGE_MENU_MAP.get("permission")
    if norm.startswith("user"):
        return PAGE_MENU_MAP.get("user")
    if norm.startswith("datasets") or norm.startswith("dataset"):
        return PAGE_MENU_MAP.get("datasets")
    if norm.startswith("access_requests"):
        return PAGE_MENU_MAP.get("access_requests")
    if norm.startswith("mfa/totp/setup"):
        return PAGE_MENU_MAP.get("mfa/totp/setup")
    return None


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
        _, info = auth_info(jwt_token)
        flags = _ensure_menu_flags(request.cookies, (info or {}).get("UserId"))
        menu_id = _path_to_menu_id(request.path)
        if menu_id and not flags.get(menu_id):
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
