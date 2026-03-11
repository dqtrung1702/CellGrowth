from flask import Blueprint, request
from werkzeug.wrappers import Response
import json
from datetime import datetime
from psycopg2.extras import RealDictCursor
import re
import jwt

from bson import json_util

from config import Config
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


def _current_user_id():
    token = request.cookies.get("app_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
    if not token:
        return None
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload.get("UserId")
    except Exception:
        return None


def _data_scope_filters(user_id, service_name="uaa", table_name="users", alias=None):
    """
    Row-level filter for DATA permission attached directly to user (data_permission_id).
    Returns (where_sql, params) or (None, None) for full access.
    """
    if not user_id:
        return None, None

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT data_permission_id FROM users WHERE id=%s;", (user_id,))
            row = cur.fetchone()
            if not row or not row.get("data_permission_id"):
                return None, None
            perm_id = row["data_permission_id"]

            cur.execute(
                """
                SELECT s.services AS "Services",
                       d.tablename AS "Table",
                       d.colname   AS "Column",
                       d.colval    AS "Value"
                FROM data_permissions dp
                JOIN permissions p ON p.id = dp.permission_id AND p.permission_type = 'DATA'
                JOIN sets s ON s.id = dp.set_id
                LEFT JOIN datasets d ON d.set_id = s.id
                WHERE dp.permission_id = %s;
                """,
                (perm_id,),
            )
            scopes = cur.fetchall()
    finally:
        _db.conn_pool.putconn(conn)

    # Ignore sets that have no dataset rows (tablename is NULL) to avoid unintended full access
    scopes = [sc for sc in scopes if sc.get("Table")]

    if not scopes:
        return "1=0", []

    service_name = (service_name or "").lower()
    table_name = (table_name or "").lower()

    filters = []
    wildcard = False
    for sc in scopes:
        svc = (sc.get("Services") or "*").lower()
        tbl = (sc.get("Table") or "*").lower()
        col = sc.get("Column") or "*"
        val = sc.get("Value") or "*"

        if svc not in ("*", service_name):
            continue
        if tbl not in ("*", table_name):
            continue
        if col == "*" or val == "*":
            wildcard = True
            continue
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", col):
            continue
        filters.append((col, val))

    if wildcard and not filters:
        return None, None  # full access
    if not filters:
        return "1=0", []   # deny all if no usable scope

    clauses = []
    params = []
    prefix = f"{alias}." if alias else ""
    for col, val in filters:
        clauses.append(f"{prefix}{col} = %s")
        params.append(val)
    return "(" + " OR ".join(clauses) + ")", params


@user_bp.route("/getUserList", methods=["POST"])
def get_user_list():
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    username_filter = data.get("UserName")
    offset = (page - 1) * page_size

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, service_name="uaa", table_name="users", alias="users")

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            where = []
            params = []
            if username_filter:
                where.append("username ILIKE %s")
                params.append(f"%{username_filter}%")
            if scope_sql:
                where.append(scope_sql)
                params.extend(scope_params)
            where_sql = "WHERE " + " AND ".join(where) if where else ""

            cur.execute(f"SELECT COUNT(*) AS count FROM users {where_sql};", params)
            total_row = cur.fetchone()["count"]

            cur.execute(
                f"""
                SELECT id,
                       username AS "UserName",
                       last_signon_datetime AS "LastSignOnDateTime",
                       updated_at AS "LastUpdateDateTime"
                FROM users
                {where_sql}
                ORDER BY id
                LIMIT %s OFFSET %s;
                """,
                params + [page_size, offset],
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

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, service_name="uaa", table_name="users", alias="u")

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            params = [user_id]
            extra = ""
            if scope_sql:
                extra = " AND " + scope_sql
                params.extend(scope_params)
            cur.execute(
                f"""
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
                WHERE u.id = %s {extra};
                """,
                params,
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
