from flask import Blueprint, request
from werkzeug.wrappers import Response
import json
from datetime import datetime
from psycopg2.extras import RealDictCursor

from bson import json_util

from models.database import db

user_bp = Blueprint("user_api", __name__)
_db = db()


def _json_response(payload, status=200):
    return Response(json.dumps(payload, default=json_util.default), mimetype="application/json", status=status)


def _hash_password(plain_password: str):
    try:
        import bcrypt

        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    except Exception:
        return plain_password.encode("utf-8")


@user_bp.route("/getUserList", methods=["POST"])
def get_user_list():
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    username_filter = data.get("UserName")
    offset = (page - 1) * page_size

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if username_filter:
                cur.execute(
                    "SELECT COUNT(*) AS count FROM users WHERE username ILIKE %s;",
                    (f"%{username_filter}%",),
                )
                total_row = cur.fetchone()["count"]
                cur.execute(
                    """
                    SELECT id,
                           username AS "UserName",
                           last_signon_datetime AS "LastSignOnDateTime",
                           updated_at AS "LastUpdateDateTime"
                    FROM users
                    WHERE username ILIKE %s
                    ORDER BY id
                    LIMIT %s OFFSET %s;
                    """,
                    (f"%{username_filter}%", page_size, offset),
                )
            else:
                cur.execute("SELECT COUNT(*) AS count FROM users;")
                total_row = cur.fetchone()["count"]

                cur.execute(
                    """
                    SELECT id,
                           username AS "UserName",
                           last_signon_datetime AS "LastSignOnDateTime",
                           updated_at AS "LastUpdateDateTime"
                    FROM users
                    ORDER BY id
                    LIMIT %s OFFSET %s;
                    """,
                    (page_size, offset),
                )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "total_row": [{"sum": total_row}], "status": "OK"})


@user_bp.route("/getUserInfo", methods=["POST"])
def get_user_info():
    data = request.get_json(silent=True) or {}
    user_id = data.get("id")
    if not user_id:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT u.id,
                       u.username AS "UserName",
                       u.userlocked AS "UserLocked",
                       u.last_signon_datetime AS "LastSignOnDateTime",
                       u.updated_at AS "LastUpdateDateTime",
                       u.username AS "LastUpdateUserName",
                       COALESCE(u.name_display, '') AS "NameDisplay",
                       u.data_permission_id AS "DataPermissionId",
                       p.code AS "DataPermissionCode"
                FROM users u
                LEFT JOIN permissions p ON p.id = u.data_permission_id
                WHERE u.id = %s;
                """,
                (user_id,),
            )
            row = cur.fetchone()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    if not row:
        return _json_response({"message": "User not found", "status": "FAIL"}, status=404)

    # đặt DataPermission hiển thị: ưu tiên code; nếu None -> ''
    row["DataPermission"] = row.get("DataPermissionCode") or ""

    return _json_response({"data": [row], "status": "OK"})


@user_bp.route("/updateUser", methods=["POST"])
def update_user():
    data = request.get_json(silent=True) or {}
    user_id = data.get("id")
    if not user_id:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    fields = []
    params = []

    user_locked = data.get("UserLocked")
    if user_locked is not None:
        fields.append("userlocked = %s")
        params.append(user_locked in ("on", True, "True", "true", 1))

    password = data.get("Password")
    if password:
        fields.append("password = %s")
        params.append(_hash_password(password))

    name_display = data.get("NameDisplay")
    if name_display is not None:
        fields.append("name_display = %s")
        params.append(name_display)

    if "DataPermission" in data:
        data_permission = data.get("DataPermission")
        # select2 có thể trả list hoặc chuỗi; cho phép clear (None/''/0 -> NULL)
        if isinstance(data_permission, (list, tuple)):
            data_permission = data_permission[0] if data_permission else None
        if data_permission in ("", None, 0, "0"):
            data_permission = None
        try:
            data_permission = int(data_permission) if data_permission is not None else None
        except Exception:
            data_permission = None
        fields.append("data_permission_id = %s")
        params.append(data_permission)

    if not fields:
        return _json_response({"message": "No fields to update", "status": "FAIL"}, status=400)

    params.append(user_id)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE users SET {', '.join(fields)}, updated_at=%s WHERE id=%s;", params[:-1] + [datetime.utcnow(), user_id])
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@user_bp.route("/updateUserRole", methods=["POST"])
def update_user_role():
    data = request.get_json(silent=True) or {}
    user_id = data.get("UserId") or data.get("id")
    role_list = data.get("RoleList") or []

    if not user_id:
        return _json_response({"message": "UserId is required", "status": "FAIL"}, status=400)

    # RoleList có thể là list role_id dạng str/int
    try:
        role_ids = [int(r) for r in role_list]
    except Exception:
        role_ids = []

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            # Xóa role cũ
            cur.execute("DELETE FROM user_roles WHERE user_id = %s;", (user_id,))
            # Thêm role mới
            for rid in role_ids:
                cur.execute(
                    """
                    INSERT INTO user_roles (user_id, role_id, last_update_datetime)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, role_id) DO NOTHING;
                    """,
                    (user_id, rid, datetime.utcnow()),
                )
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})
