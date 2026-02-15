from flask import Flask
from flask import request, jsonify
from flask_session import Session
from config import Config
from models.database import db
from modules.Authentication import authentication
from modules.User import user_bp
from modules.RolePermission import rp_bp

app = Flask(__name__)  # khởi tạo app
app.config.from_object(Config)  # đưa các thông tin từ config vào app

# Kích hoạt server-side session (Redis theo cấu hình trong Config)
Session(app)

app.register_blueprint(authentication)
app.register_blueprint(user_bp)
app.register_blueprint(rp_bp)

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

    # Cho phép login/register không cần token; mọi đường khác bắt buộc có token + URL permission
    public_paths = {"/login", "/register"}
    if not token:
        if path in public_paths:
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

    conn = _pool.conn_pool.getconn()
    ok = None
    try:
        with conn.cursor() as cur:
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
                (user_id, method, '%', path),
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
