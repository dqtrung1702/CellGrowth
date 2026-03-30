import os

from flask import Flask
from flask import request, jsonify, send_from_directory
from flask_session import Session
from config import Config
from models.database import db
from controllers.Authentication import authentication
from controllers.User import user_bp
from controllers.Role import role_bp
from controllers.URL import url_bp
from controllers.Data import data_bp
from controllers.Set import set_bp
from controllers.AccessRequest import ar_bp
from controllers.Mfa import mfa_bp
from services.authorization_service import AuthorizationService
from utils.token import extract_token
from utils.http import json_response
from schemas.response import ResponseEnvelope
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time

app = Flask(__name__)  # khởi tạo app
app.config.from_object(Config)  # đưa các thông tin từ config vào app

# Kích hoạt server-side session (Redis theo cấu hình trong Config)
Session(app)


def _ensure_redis_alive():
    redis_client = app.config.get("SESSION_REDIS")
    if not redis_client:
        raise SystemExit("SESSION_REDIS is not configured")
    try:
        redis_client.ping()
    except Exception as exc:  # pragma: no cover - defensive
        print("REDIS_HEALTHCHECK_FAIL", exc)
        raise SystemExit(1)


if not os.getenv("UAA_SKIP_REDIS_HEALTHCHECK"):
    _ensure_redis_alive()

app.register_blueprint(authentication)
app.register_blueprint(user_bp)
app.register_blueprint(role_bp)
app.register_blueprint(url_bp)
app.register_blueprint(data_bp)
app.register_blueprint(set_bp)
app.register_blueprint(ar_bp)
app.register_blueprint(mfa_bp)

START_TIME = time.time()

if os.getenv("UAA_SKIP_DB_INIT"):
    _pool = None
    _authz = None
else:
    _pool = db()
    _authz = AuthorizationService()


class PrefixMiddleware:
    """
    Cho phép truy cập cả /api/v1/... lẫn đường dẫn legacy.
    Nếu PATH_INFO bắt đầu bằng /api/v1 thì strip prefix và forward.
    """

    def __init__(self, app, prefix="/api/v1"):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith(self.prefix):
            environ["PATH_INFO"] = path[len(self.prefix):] or "/"
        return self.app(environ, start_response)


app.wsgi_app = PrefixMiddleware(app.wsgi_app)  # type: ignore


@app.before_request
def enforce_url_permission():
    token = extract_token()
    path = request.path
    if request.method.upper() == "OPTIONS":
        return "", 204

    is_public = path in Config.PUBLIC_ENDPOINTS or any(path.startswith(prefix) for prefix in Config.PUBLIC_PREFIXES)
    if is_public:
        # Cho phép toàn bộ public endpoint/prefix bỏ qua authz
        return

    if not token:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        import jwt

        auth_info = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except Exception:
        return jsonify({"message": "Token invalid"}), 401

    user_id = auth_info.get("UserId")
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    method = request.method.upper()

    # Cho phép mọi user đã đăng nhập truy cập/ghi access_requests của chính họ mà không cần PAGE permission.
    # - list + create: /access_requests (GET/POST)
    # - view chi tiết: GET /access_requests/<id>
    # - update/cancel: POST /access_requests/<id>/update hoặc /cancel (service tự kiểm tra owner)
    if path == "/access_requests":
        return
    if path.startswith("/access_requests/"):
        parts = path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "access_requests" and parts[1].isdigit():
            if method == "GET":
                return
            if method == "POST" and len(parts) == 3 and parts[2] in ("update", "cancel"):
                return

    if _authz and not _authz.has_url_access(user_id, path, method):
        return jsonify({"message": "Access is denied", "status": "FAIL"}), 403

@app.route("/docs")
def swagger_ui():
    return send_from_directory("static/swagger", "index.html")

@app.route("/swagger/<path:filename>")
def swagger_assets(filename):
    return send_from_directory("static/swagger", filename)

@app.route("/openapi.yaml")
def swagger_spec():
    return send_from_directory("static/swagger", "openapi.yaml")

@app.route("/status", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    uptime = int(time.time() - START_TIME)
    resp = json_response(ResponseEnvelope(status="OK", data={"service": "uaa", "uptime_seconds": uptime}))
    # CORS cho health check (dùng ở frontend http://localhost:5003)
    origin = request.headers.get("Origin")
    if origin:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp

@app.route('/')
def index():
    return 'The User Authentication and Authorization(UAA) services provides role-based access control (RBAC) for both internal services and user-facing applications. Although the UAA can use an internal identity store (e.g. MySQL or PostgreSQL), typically an external identity provider (IdP) is used.'

if __name__ == '__main__':
    app.run(Config.UAA_IP, Config.UAA_PORT,Config.UAA_DEBUG_MODE)
