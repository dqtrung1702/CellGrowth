from flask import Flask
from flask import request, jsonify
from flask_session import Session
from config import Config
from models.database import db
from modules.Authentication import authentication
from modules.User import user_bp
from modules.RolePermission import rp_bp
from modules.AccessRequest import ar_bp

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


_ensure_redis_alive()

app.register_blueprint(authentication)
app.register_blueprint(user_bp)
app.register_blueprint(rp_bp)
app.register_blueprint(ar_bp)

_pool = db()


def _extract_token():
    jwt_token = request.cookies.get("app_token")
    if not jwt_token:
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            jwt_token = parts[1]
    return jwt_token


@app.before_request
def enforce_url_permission():
    token = _extract_token()
    path = request.path
    if request.method.upper() == "OPTIONS":
        return "", 204

    # Cho phép một số endpoint công khai (login/register/status/health/ping)
    public_paths = {
        "/login",
        "/register",
        "/status",
        "/health",
        "/ping",
        "/favicon.ico",
        "/getPageByUser",
        "/getDataSetByUser",
        "/publicRoleList",
        "/publicPermissionList",
    }
    # cho phép cả /status/... hoặc /healthz và toàn bộ static
    public_prefixes = ("/status", "/health", "/static")
    if not token:
        if path in public_paths or path.startswith(public_prefixes):
            return
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

    # Cho phép mọi user đã đăng nhập truy cập danh sách access_requests (GET/POST) để tự xem/gửi request
    if path == "/access_requests":
        return

    conn = _pool.conn_pool.getconn()
    ok = None
    try:
        with conn.cursor() as cur:
            # Kiểm tra quyền truy cập URL: khớp chính xác hoặc theo pattern (up.url có thể chứa wildcard %/_).
            cur.execute(
                """
                SELECT 1
                FROM user_roles ur
                JOIN role_permissions rp ON rp.role_id = ur.role_id
                JOIN url_permissions up ON up.permission_id = rp.permission_id
                WHERE ur.user_id = %s
                  AND (up.method = '*' OR upper(up.method) = %s)
                  AND (up.url = %s OR %s LIKE up.url)
                LIMIT 1;
                """,
                (user_id, method, path, path),
            )
            ok = cur.fetchone()
            print("AUTHZ_CHECK", {"user_id": user_id, "path": path, "method": method, "ok": ok})
    except Exception as e:
        print("AUTHZ_ERR", e)
        ok = None
    finally:
        _pool.conn_pool.putconn(conn)

    if not ok:
        return jsonify({"message": "Access is denied", "status": "FAIL"}), 403

@app.route('/')
def index():
    return 'The User Authentication and Authorization(UAA) services provides role-based access control (RBAC) for both internal services and user-facing applications. Although the UAA can use an internal identity store (e.g. MySQL or PostgreSQL), typically an external identity provider (IdP) is used.'

if __name__ == '__main__':
    app.run(Config.UAA_IP, Config.UAA_PORT,Config.UAA_DEBUG_MODE)
