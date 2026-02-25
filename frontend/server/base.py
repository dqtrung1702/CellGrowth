from functools import wraps
import secrets

from flask import request, redirect, session, abort
from config import Config
import jwt
def auth(jwt_token):
    try:
      auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
      if auth_info:
        return True
    except:
      return False

def auth_info(jwt_token):
    try:
      auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
      if auth_info:
        return True,auth_info
    except:
      return False,None
def check_url(URLList, url, **kwargs):
    url_norm = (url or '').strip().lower()
    for xURL in URLList:
      if (xURL.get('url') or '').strip().lower() == url_norm:
        xlist = []
        ylist = []
        for key, value in kwargs.items():
          xlist.append(xURL.get(key))
          ylist.append(value)
        pairs = zip(xlist, ylist)
        if not any(x != y for x, y in pairs):
          return True
    return False


def require_page_access(view_func):
    """
    Decorator: kiểm tra JWT + quyền URL dựa trên URLList lưu trong session.
    - Nếu chưa đăng nhập: redirect Accessisdenied.
    - Nếu có URLList và không khớp quyền: redirect Accessisdenied.
    - Nếu không có URLList (chưa nạp), cho phép tạm để tránh kẹt vòng lặp; UAA vẫn chặn ở backend.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        jwt_token = request.cookies.get('app_token','')
        if not auth(jwt_token):
            return redirect('Accessisdenied')
        url_list = session.get('URLList')
        # Chỉ enforce page-level ACL nếu backend thực sự cung cấp rule Type='page'
        has_page_rules = url_list and any((item or {}).get('Type') == 'page' for item in url_list)
        # Use path instead of full base_url to match entries stored from backend
        if has_page_rules and not check_url(url_list, request.path, Method=request.method, Type='page'):
            return redirect('Accessisdenied')
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
          
# def Pagination():
