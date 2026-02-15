from datetime import datetime, timedelta
import json

from flask import Blueprint, request, session
from werkzeug.wrappers import Response
from bson import json_util
import jwt
from psycopg2.extras import RealDictCursor

from config import Config
from models.database import db

# Khởi tạo pool kết nối Postgres dùng psycopg2
_db = db()

authentication = Blueprint("authentication", __name__)


def _verify_password(stored_password, provided_password: str) -> bool:
    """Kiểm tra mật khẩu, ưu tiên bcrypt nếu có; fallback so sánh chuỗi/plaintext."""
    if stored_password is None:
        return False

    # Chuẩn hóa kiểu dữ liệu
    if isinstance(stored_password, memoryview):
        stored_password = stored_password.tobytes()
    elif isinstance(stored_password, bytearray):
        stored_password = bytes(stored_password)

    try:
        import bcrypt

        if isinstance(stored_password, (bytes, bytearray)):
            return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password)
    except Exception:
        # Không có bcrypt hoặc lỗi, thử tiếp phương án khác
        pass

    if isinstance(stored_password, bytes):
        try:
            return stored_password.decode("utf-8") == provided_password
        except Exception:
            return False

    return str(stored_password) == provided_password


def _hash_password(plain_password: str):
    """Tạo hash bcrypt nếu có, ngược lại lưu plaintext bytes (kém an toàn nhưng vẫn chạy)."""
    try:
        import bcrypt

        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    except Exception:
        return plain_password.encode("utf-8")


def _fetch_user(username: str):
    """Lấy thông tin user từ bảng users theo username."""
    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, password, userlocked
                FROM users
                WHERE username = %s
                LIMIT 1;
                """,
                (username,),
            )
            user = cur.fetchone()
            conn.commit()
            return user
    finally:
        _db.conn_pool.putconn(conn)


def _update_last_signon(user_id: int):
    """Cập nhật thời điểm đăng nhập gần nhất."""
    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET last_signon_datetime = %s WHERE id = %s;",
                (datetime.utcnow(), user_id),
            )
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)


@authentication.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        res = json.dumps(
            {"message": "Request no content", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=400)

    username = (data.get("UserName") or data.get("username") or "").strip()
    password = data.get("Password") or data.get("password")

    if not username or not password:
        res = json.dumps(
            {"message": "UserName and Password are required", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=400)

    user = _fetch_user(username)
    if not user:
        res = json.dumps(
            {"message": "User is incorrect", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=200)

    if user.get("userlocked"):
        res = json.dumps(
            {"message": "User is locked", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=200)

    if not _verify_password(user.get("password"), password):
        res = json.dumps(
            {"message": "Password is incorrect", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=200)

    _update_last_signon(user["id"])

    payload = {
        "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS),
        "UserId": user["id"],
        "UserName": username,
    }
    jwt_token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    token_str = jwt_token if isinstance(jwt_token, str) else jwt_token.decode("utf-8")

    session["UserId"] = user["id"]
    session["UserName"] = username

    res_body = {"token": token_str, "status": "OK"}
    res = json.dumps(res_body, default=json_util.default)
    return Response(res, mimetype="application/json", status=200)


@authentication.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        res = json.dumps(
            {"message": "Request no content", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=400)

    username = (data.get("UserName") or data.get("username") or data.get("Code") or "").strip()
    password = data.get("Password") or data.get("password")
    name_display = data.get("NameDisplay") or data.get("namedisplay") or ""

    if not username or not password:
        res = json.dumps(
            {"message": "UserName and Password are required", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=400)

    if _fetch_user(username):
        res = json.dumps(
            {"message": "UserName is existed", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=200)

    hashed = _hash_password(password)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO users (username, password, userlocked, last_signon_datetime, created_at, updated_at)
                VALUES (%s, %s, TRUE, %s, NOW(), NOW())
                RETURNING id;
                """,
                (username, hashed, datetime.utcnow()),
            )
            row = cur.fetchone()
            conn.commit()
            user_id = row["id"] if row else None
    except Exception as e:
        conn.rollback()
        res = json.dumps(
            {"message": f"Register failed: {e}", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=500)
    finally:
        _db.conn_pool.putconn(conn)

    payload = {
        "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS),
        "UserId": user_id,
        "UserName": username,
    }
    jwt_token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    token_str = jwt_token if isinstance(jwt_token, str) else jwt_token.decode("utf-8")

    session["UserId"] = user_id
    session["UserName"] = username
    session["NameDisplay"] = name_display

    res_body = {"token": token_str, "status": "OK"}
    res = json.dumps(res_body, default=json_util.default)
    return Response(res, mimetype="application/json", status=200)


@authentication.route("/check_auth_ext", methods=["POST"])
def check_auth_ext():
    jwt_token = request.cookies.get("app_token")
    if not jwt_token:
        # Thử lấy từ header Authorization nếu không có cookie
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            jwt_token = auth_header.split(None, 1)[1]

    if not jwt_token:
        res = json.dumps(
            {"message": "Access is denied", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=401)

    try:
        auth_info = jwt.decode(
            jwt_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
    except Exception:
        res = json.dumps(
            {"message": "Token is invalid", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=401)

    user_id = auth_info.get("UserId")
    if session.get("UserId") != user_id:
        res = json.dumps(
            {"message": "Access is denied", "status": "FAIL"},
            default=json_util.default,
        )
        return Response(res, mimetype="application/json", status=401)

    payload = {
        "UserId": user_id,
        "UserName": session.get("UserName", ""),
    }
    res = json.dumps({"data": payload, "status": "OK"}, default=json_util.default)
    return Response(res, mimetype="application/json", status=200)
