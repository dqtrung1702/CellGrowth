from flask import Blueprint, request
from werkzeug.wrappers import Response
import json
from psycopg2.extras import RealDictCursor
from psycopg2 import errors
from bson import json_util
from datetime import datetime
import jwt
import re

from config import Config
from models.database import db

rp_bp = Blueprint("role_permission_api", __name__)
_db = db()


def _json_response(payload, status=200):
    return Response(json.dumps(payload, default=json_util.default), mimetype="application/json", status=status)


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


def _data_scope_filters(user_id, table_name, service_name="uaa"):
    """
    Build row-level filter from data_permission_id attached to requesting user.
    Returns (where_sql, params); if user has no data_permission_id or scopes, deny all (1=0).
    """
    if not user_id:
        return "1=0", []

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT data_permission_id FROM users WHERE id=%s;", (user_id,))
            row = cur.fetchone()
            if not row or not row.get("data_permission_id"):
                return "1=0", []
            perm_id = row["data_permission_id"]

            cur.execute(
                """
                SELECT s.services AS "Services",
                       COALESCE(d.tablename, '*') AS "Table",
                       COALESCE(d.colname, '*')   AS "Column",
                       COALESCE(d.colval, '*')    AS "Value"
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
    for col, val in filters:
        clauses.append(f"{col} = %s")
        params.append(val)
    return "(" + " OR ".join(clauses) + ")", params


def _ensure_set(cur, set_entry):
    """Insert set if not exists, return set_id."""
    setname = (set_entry.get("setname") or set_entry.get("SetName") or set_entry.get("name") or "").strip()
    services = (
        set_entry.get("services")
        or set_entry.get("Services")
        or set_entry.get("service")
        or set_entry.get("Service")
        or ""
    )
    services = services.strip() if isinstance(services, str) else services
    setcode = (set_entry.get("setcode") or set_entry.get("SetCode") or set_entry.get("code") or "").strip()

    # Ngăn scope rỗng: bắt buộc đủ 3 trường và không được là '*' / ''
    if not setname or not services or not setcode or setcode == "*":
        raise ValueError("SetName, Services, SetCode là bắt buộc và không được để trống hoặc '*'.")
    tbl = set_entry.get("table") or set_entry.get("Table") or set_entry.get("tbl") or set_entry.get("TableName")
    col = set_entry.get("column") or set_entry.get("Column") or set_entry.get("col") or set_entry.get("ColumnName")
    val = set_entry.get("value") or set_entry.get("Value") or set_entry.get("val")
    # validation-only mode (used when cur is None)
    if cur is None:
        return None

    cur.execute(
        """
        INSERT INTO sets (setname, services, setcode)
        VALUES (%s,%s,%s)
        ON CONFLICT (setname, services, setcode)
        DO UPDATE SET setname=EXCLUDED.setname, services=EXCLUDED.services, setcode=EXCLUDED.setcode
        RETURNING id;
        """,
        (setname, services, setcode),
    )
    set_id = cur.fetchone()[0]

    # Optionally attach dataset definition to this set (chỉ khi có cursor)
    if cur and tbl and col and val:
        cur.execute(
            """
            INSERT INTO datasets (set_id, tablename, colname, colval)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (set_id, tablename, colname, colval) DO NOTHING;
            """,
            (set_id, tbl, col, val),
        )

    return set_id


def _resolve_set_id(cur, set_entry):
    """Validate an existing set_id from payload; do not create/update sets here."""
    sid = (
        set_entry.get("SetId")
        or set_entry.get("set_id")
        or set_entry.get("id")
        or set_entry.get("Id")
    )
    try:
        sid = int(sid)
    except Exception:
        raise ValueError("SetId is required for DATA permission.")

    cur.execute("SELECT id FROM sets WHERE id=%s;", (sid,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"SetId {sid} không tồn tại.")
    return sid


@rp_bp.route("/getRoleList", methods=["POST"])
def get_role_list():
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    code = data.get("Code")
    offset = (page - 1) * page_size

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, table_name="roles")

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            where = []
            params = []
            if code:
                where.append("code ILIKE %s")
                params.append(f"%{code}%")
            if scope_sql:
                where.append(scope_sql)
                params.extend(scope_params)
            where_sql = "WHERE " + " AND ".join(where) if where else ""

            cur.execute(f"SELECT COUNT(*) AS count FROM roles {where_sql};", params)
            total = cur.fetchone()["count"]

            cur.execute(
                f"""
                SELECT id, code AS "Code", description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM roles
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

    return _json_response({"data": rows, "total_row": [{"sum": total}], "status": "OK"})


@rp_bp.route("/getRoleInfo", methods=["POST"])
def get_role_info():
    data = request.get_json(silent=True) or {}
    role_id = data.get("id")
    if not role_id:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, table_name="roles")

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id, code AS "Code", description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM roles WHERE id = %s {(' AND ' + scope_sql) if scope_sql else ''};
                """,
                [role_id] + (scope_params or []),
            )
            row = cur.fetchone()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    if not row:
        return _json_response({"message": "Role not found", "status": "FAIL"}, status=404)
    return _json_response({"data": [row], "status": "OK"})


@rp_bp.route("/addRole", methods=["POST"])
def add_role():
    data = request.get_json(silent=True) or {}
    code = data.get("Code")
    description = data.get("Description")
    permissions = data.get("Permission") or []

    if not code:
        return _json_response({"message": "Code is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO roles (code, description, last_update_username, last_update_datetime)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (code, description, "system", datetime.utcnow()),
            )
            rid = cur.fetchone()[0]
            # assign permissions
            for pid in permissions:
                try:
                    pid_int = int(pid)
                except Exception:
                    continue
                cur.execute(
                    """
                    INSERT INTO role_permissions (role_id, permission_id, last_update_datetime)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (role_id, permission_id) DO NOTHING;
                    """,
                    (rid, pid_int, datetime.utcnow()),
                )
            conn.commit()
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": {"id": rid}, "status": "OK"})


@rp_bp.route("/updateRole", methods=["POST"])
def update_role():
    data = request.get_json(silent=True) or {}
    rid = data.get("RoleId")
    if not rid:
        return _json_response({"message": "RoleId is required", "status": "FAIL"}, status=400)

    description = data.get("Description")
    permissions = data.get("Permission") or []

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            if description is not None:
                cur.execute(
                    "UPDATE roles SET description=%s, last_update_datetime=%s WHERE id=%s;",
                    (description, datetime.utcnow(), rid),
                )
            # reset permissions
            cur.execute("DELETE FROM role_permissions WHERE role_id=%s;", (rid,))
            for pid in permissions:
                try:
                    pid_int = int(pid)
                except Exception:
                    continue
                cur.execute(
                    """
                    INSERT INTO role_permissions (role_id, permission_id, last_update_datetime)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (role_id, permission_id) DO NOTHING;
                    """,
                    (rid, pid_int, datetime.utcnow()),
                )
            conn.commit()
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/deleteRoleById", methods=["POST"])
def delete_role():
    data = request.get_json(silent=True) or {}
    rid = data.get("id")
    if not rid:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM roles WHERE id=%s;", (rid,))
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/getPermissionByRole", methods=["POST"])
def get_permission_by_role():
    data = request.get_json(silent=True) or {}
    rid = data.get("id")
    if not rid:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT p.id AS "PermissionId", p.code AS "PermissionName"
                FROM role_permissions rp
                JOIN permissions p ON p.id = rp.permission_id
                WHERE rp.role_id = %s;
                """,
                (rid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getDataSetByUser", methods=["POST"])
def get_dataset_by_user():
    """Return all data scopes (sets/datasets) effective for a given user via their roles."""
    data = request.get_json(silent=True) or {}
    uid = data.get("UserId") or data.get("user_id")
    if not uid:
        return _json_response({"message": "UserId is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT
                    s.id AS "SetId",
                    s.setname AS "SetName",
                    s.services AS "Services",
                    s.setcode AS "SetCode",
                    d.tablename AS "Table",
                    d.colname AS "Column",
                    d.colval AS "Value"
                FROM user_roles ur
                JOIN role_permissions rp ON rp.role_id = ur.role_id
                JOIN permissions p ON p.id = rp.permission_id AND p.permission_type = 'DATA'
                JOIN data_permissions dp ON dp.permission_id = p.id
                JOIN sets s ON s.id = dp.set_id
                LEFT JOIN datasets d ON d.set_id = s.id
                WHERE ur.user_id = %s;
                """,
                (uid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getSetList", methods=["POST"])
def get_set_list():
    """Return all sets (optionally filtered by setname/services/setcode) with data-scope enforcement."""
    data = request.get_json(silent=True) or {}
    setname = data.get("SetName")
    services = data.get("Services")
    setcode = data.get("SetCode")

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, table_name="sets")

    where = []
    params = []
    if setname:
        where.append("setname ILIKE %s")
        params.append(f"%{setname}%")
    if services:
        where.append("services ILIKE %s")
        params.append(f"%{services}%")
    if setcode:
        where.append("setcode ILIKE %s")
        params.append(f"%{setcode}%")
    if scope_sql:
        where.append(scope_sql)
        params.extend(scope_params)
    where_sql = "WHERE " + " AND ".join(where) if where else ""

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id AS "SetId", setname AS "SetName", services AS "Services", setcode AS "SetCode"
                FROM sets
                {where_sql}
                ORDER BY id;
                """,
                params,
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/addSet", methods=["POST"])
def add_set():
    """Tạo mới một Set (SetName/Services/SetCode)."""
    data = request.get_json(silent=True) or {}
    setname = data.get("SetName") or data.get("setname")
    services = data.get("Services") or data.get("services")
    setcode = data.get("SetCode") or data.get("setcode")
    payload = {"SetName": setname, "Services": services, "SetCode": setcode}

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            set_id = _ensure_set(cur, payload)
            conn.commit()
    except ValueError as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=400)
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": {"SetId": set_id}, "status": "OK"})


@rp_bp.route("/updateSet", methods=["POST"])
def update_set():
    """Cập nhật SetName/Services/SetCode của một set."""
    data = request.get_json(silent=True) or {}
    set_id = data.get("SetId") or data.get("id")
    if not set_id:
        return _json_response({"message": "SetId is required", "status": "FAIL"}, status=400)

    setname = data.get("SetName") or data.get("setname")
    services = data.get("Services") or data.get("services")
    setcode = data.get("SetCode") or data.get("setcode")

    # validate
    tmp_payload = {"SetName": setname, "Services": services, "SetCode": setcode}
    try:
        _ensure_set(cur=None, set_entry=tmp_payload)  # validation only
    except ValueError as e:
        return _json_response({"message": str(e), "status": "FAIL"}, status=400)

    # real update
    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            # manual validation duplicate call
            if not setname or not services or not setcode or setcode == "*":
                raise ValueError("SetName, Services, SetCode là bắt buộc và không được để trống hoặc '*'.")
            cur.execute(
                """
                UPDATE sets
                SET setname=%s, services=%s, setcode=%s
                WHERE id=%s;
                """,
                (setname, services, setcode, set_id),
            )
            conn.commit()
    except errors.UniqueViolation:
        conn.rollback()
        return _json_response({"message": "Set trùng (SetName, Services, SetCode)", "status": "FAIL"}, status=409)
    except ValueError as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=400)
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/deleteSetById", methods=["POST"])
def delete_set_by_id():
    data = request.get_json(silent=True) or {}
    sid = data.get("SetId") or data.get("id")
    if not sid:
        return _json_response({"message": "SetId is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sets WHERE id=%s;", (sid,))
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/getDatasetBySet", methods=["POST"])
def get_dataset_by_set():
    data = request.get_json(silent=True) or {}
    sid = data.get("SetId")
    if not sid:
        return _json_response({"message": "SetId is required", "status": "FAIL"}, status=400)

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, table_name="sets")
    if scope_sql:
        conn = _db.conn_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM sets WHERE id=%s AND {scope_sql};", [sid] + scope_params)
                ok = cur.fetchone()
        finally:
            _db.conn_pool.putconn(conn)
        if not ok:
            return _json_response({"message": "Access denied", "status": "FAIL"}, status=403)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id AS "Id", set_id AS "SetId", tablename AS "Table", colname AS "Column", colval AS "Value"
                FROM datasets
                WHERE set_id = %s
                ORDER BY id;
                """,
                (sid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getDatasetByPermission", methods=["POST"])
def get_dataset_by_permission():
    data = request.get_json(silent=True) or {}
    pid = data.get("PermissionId")
    if not pid:
        return _json_response({"message": "PermissionId is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT s.id AS "SetId",
                       s.setname AS "SetName",
                       s.services AS "Services",
                       s.setcode AS "SetCode",
                       d.tablename AS "Table",
                       d.colname AS "Column",
                       d.colval AS "Value"
                FROM data_permissions dp
                JOIN permissions p ON p.id = dp.permission_id AND p.permission_type = 'DATA'
                JOIN sets s ON s.id = dp.set_id
                LEFT JOIN datasets d ON d.set_id = s.id
                WHERE dp.permission_id = %s
                ORDER BY s.id, d.id;
                """,
                (pid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/updateDatasetBySet", methods=["POST"])
def update_dataset_by_set():
    data = request.get_json(silent=True) or {}
    sid = data.get("SetId")
    items = data.get("Data") or []
    if not sid:
        return _json_response({"message": "SetId is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM datasets WHERE set_id = %s;", (sid,))
            for it in items:
                table = (it.get("Table") or "*").strip()
                col = (it.get("Column") or "*").strip()
                val = (it.get("Value") or "*").strip()
                cur.execute(
                    """
                    INSERT INTO datasets (set_id, tablename, colname, colval)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (set_id, tablename, colname, colval) DO NOTHING;
                    """,
                    (sid, table, col, val),
                )
            conn.commit()
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/getUserByRole", methods=["POST"])
def get_user_by_role():
    data = request.get_json(silent=True) or {}
    rid = data.get("id")
    if not rid:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT u.username AS "UserName"
                FROM user_roles ur
                JOIN users u ON u.id = ur.user_id
                WHERE ur.role_id = %s;
                """,
                (rid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getRoleByUser", methods=["POST"])
def get_role_by_user():
    data = request.get_json(silent=True) or {}
    uid = data.get("id") or data.get("UserId")
    if not uid:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT r.id AS "RoleId", r.code AS "Role"
                FROM user_roles ur
                JOIN roles r ON r.id = ur.role_id
                WHERE ur.user_id = %s;
                """,
                (uid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getPermissionList", methods=["POST"])
def get_permission_list():
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    code = data.get("Code")
    ptype_raw = data.get("PermissionType")
    ptype_list = None
    if isinstance(ptype_raw, (list, tuple, set)):
        ptype_list = [str(p).upper() for p in ptype_raw]
    elif ptype_raw:
        p = str(ptype_raw).upper()
        ptype_list = [p] if p else None
    offset = (page - 1) * page_size

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, table_name="permissions")

    where = []
    params = []
    if code:
        where.append("code ILIKE %s")
        params.append(f"%{code}%")
    if ptype_list:
        if len(ptype_list) == 1:
            where.append("permission_type = %s")
            params.append(ptype_list[0])
        else:
            where.append("permission_type = ANY(%s)")
            params.append(ptype_list)
    if scope_sql:
        where.append(scope_sql)
        params.extend(scope_params)
    where_sql = "WHERE " + " AND ".join(where) if where else ""

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT COUNT(*) AS count FROM permissions {where_sql};", params)
            total = cur.fetchone()["count"]
            cur.execute(
                f"""
                SELECT id, code AS "Code", permission_type AS "PermissionType",
                       description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM permissions
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

    return _json_response({"data": rows, "total_row": [{"sum": total}], "status": "OK"})


@rp_bp.route("/getPermissionInfo", methods=["POST"])
def get_permission_info():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not ids:
        return _json_response({"data": [], "status": "OK"})
    try:
        ids_int = [int(i) for i in ids]
    except Exception:
        ids_int = []

    requester_id = _current_user_id()
    scope_sql, scope_params = _data_scope_filters(requester_id, table_name="permissions")

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id AS "id", code AS "Code", code AS "PermissionName",
                       permission_type AS "PermissionType",
                       description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM permissions
                WHERE id = ANY(%s) {(' AND ' + scope_sql) if scope_sql else ''};
                """,
                [ids_int] + (scope_params or []),
            )
            rows = cur.fetchall()
            # attach DataSets if DATA type
            # Step 1: fetch distinct sets for requested permissions
            cur.execute(
                """
                SELECT DISTINCT dp.permission_id,
                                s.id AS set_id,
                                s.setname,
                                s.services,
                                s.setcode
                FROM data_permissions dp
                JOIN sets s ON s.id = dp.set_id
                WHERE dp.permission_id = ANY(%s);
                """,
                (ids_int,),
            )
            set_rows = cur.fetchall()

            # Step 2: fetch dataset rows for these sets
            set_ids = [r["set_id"] for r in set_rows]
            data_by_set = {}
            if set_ids:
                cur.execute(
                    """
                    SELECT set_id, tablename, colname, colval
                    FROM datasets
                    WHERE set_id = ANY(%s);
                    """,
                    (set_ids,),
                )
                for r in cur.fetchall():
                    data_by_set.setdefault(r["set_id"], []).append(
                        {
                            "Table": r["tablename"],
                            "Column": r["colname"],
                            "Value": r["colval"],
                        }
                    )

            if set_rows:
                by_pid = {}
                for r in set_rows:
                    pid = r["permission_id"]
                    set_id = r["set_id"]
                    ds_entry = {
                        "SetId": set_id,
                        "SetName": r["setname"],
                        "Services": r["services"],
                        "SetCode": r["setcode"],
                    }
                    if set_id in data_by_set:
                        ds_entry["Data"] = data_by_set[set_id]
                    by_pid.setdefault(pid, []).append(ds_entry)

                for row in rows:
                    pid = row["id"]
                    row["DataSets"] = by_pid.get(pid, [])
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/addPermission", methods=["POST"])
def add_permission():
    data = request.get_json(silent=True) or {}
    code = data.get("Code")
    ptype_raw = (data.get("PermissionType") or "ROLE").upper()
    ptype = "DATA" if ptype_raw == "DATA" else "ROLE"
    description = data.get("Description")
    url_list = data.get("UrlList") or []
    data_sets = data.get("DataSets") or []

    if not code or not ptype:
        return _json_response({"message": "Code and PermissionType are required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO permissions (code, permission_type, description, last_update_username, last_update_datetime)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (code, ptype, description, "system", datetime.utcnow()),
            )
            pid = cur.fetchone()[0]
            if ptype == "DATA":
                for ds in data_sets:
                    set_id = _resolve_set_id(cur, ds if isinstance(ds, dict) else {})
                    cur.execute(
                        """
                        INSERT INTO data_permissions (permission_id, set_id, last_update_datetime)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (permission_id, set_id) DO NOTHING;
                        """,
                        (pid, set_id, datetime.utcnow()),
                    )
            else:
                for entry in url_list:
                    is_page = False
                    if isinstance(entry, dict):
                        type_val_raw = (entry.get("Type") or entry.get("type") or "").upper()
                        page_val = (
                            entry.get("page")
                            or entry.get("Page")
                            or ""
                        )
                        is_page = type_val_raw == "PAGE" or bool(page_val)
                    else:
                        page_val = ""
                        type_val_raw = ""
                    if is_page:
                        if isinstance(entry, dict):
                            page_val = page_val or entry.get("url") or entry.get("Url") or ""
                        else:
                            page_val = str(entry)
                        if not page_val:
                            continue
                        cur.execute(
                            """
                            INSERT INTO page_permissions (permission_id, page, last_update_datetime)
                            VALUES (%s, %s, %s);
                            """,
                            (pid, page_val, datetime.utcnow()),
                        )
                    else:
                        if isinstance(entry, dict):
                            url_val = entry.get("url") or entry.get("Url") or ""
                            method_val = (entry.get("Method") or entry.get("method") or "GET").upper()
                            type_val = type_val_raw or "ROLE"
                        else:
                            url_val = str(entry)
                            method_val = "GET"
                            type_val = "ROLE"
                        if not url_val:
                            continue
                        cur.execute(
                            """
                            INSERT INTO url_permissions (permission_id, url, method, type, last_update_datetime)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (pid, url_val, method_val, type_val, datetime.utcnow()),
                        )
            conn.commit()
    except errors.UniqueViolation:
        conn.rollback()
        return _json_response({"message": "Permission code already exists", "status": "FAIL"}, status=409)
    except ValueError as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=400)
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": {"id": pid}, "status": "OK"})


@rp_bp.route("/updatePermission", methods=["POST"])
def update_permission():
    data = request.get_json(silent=True) or {}
    pid = data.get("PermissionId")
    if not pid:
        return _json_response({"message": "PermissionId is required", "status": "FAIL"}, status=400)

    description = data.get("Description")
    ptype_raw = data.get("PermissionType")
    if ptype_raw is not None:
        ptype_raw = str(ptype_raw).upper()
    ptype = "DATA" if ptype_raw == "DATA" else ("ROLE" if ptype_raw else None)
    url_list = data.get("UrlList") or []
    data_sets = data.get("DataSets") or []

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            # fetch current permission_type if not provided
            if ptype is None:
                cur.execute("SELECT permission_type FROM permissions WHERE id=%s;", (pid,))
                row = cur.fetchone()
                current_ptype = (row[0] if row else "ROLE")
                ptype = "DATA" if str(current_ptype).upper() == "DATA" else "ROLE"
            if description is not None or ptype is not None:
                cur.execute(
                    """
                    UPDATE permissions
                    SET description = COALESCE(%s, description),
                        permission_type = COALESCE(%s, permission_type),
                        last_update_datetime = %s
                    WHERE id = %s;
                    """,
                    (description, ptype, datetime.utcnow(), pid),
                )
            # reset url/data/page list
            cur.execute("DELETE FROM url_permissions WHERE permission_id=%s;", (pid,))
            cur.execute("DELETE FROM data_permissions WHERE permission_id=%s;", (pid,))
            cur.execute("DELETE FROM page_permissions WHERE permission_id=%s;", (pid,))
            if ptype == "DATA":
                for ds in data_sets:
                    set_id = _resolve_set_id(cur, ds if isinstance(ds, dict) else {})
                    cur.execute(
                        """
                        INSERT INTO data_permissions (permission_id, set_id, last_update_datetime)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (permission_id, set_id) DO NOTHING;
                        """,
                        (pid, set_id, datetime.utcnow()),
                    )
            else:
                for entry in url_list:
                    is_page = False
                    if isinstance(entry, dict):
                        type_val_raw = (entry.get("Type") or entry.get("type") or "").upper()
                        page_val = entry.get("page") or entry.get("Page") or ""
                        is_page = type_val_raw == "PAGE" or bool(page_val)
                    else:
                        type_val_raw = ""
                        page_val = ""
                    if is_page:
                        if isinstance(entry, dict):
                            page_val = page_val or entry.get("url") or entry.get("Url") or ""
                        else:
                            page_val = str(entry)
                        if not page_val:
                            continue
                        cur.execute(
                            """
                            INSERT INTO page_permissions (permission_id, page, last_update_datetime)
                            VALUES (%s, %s, %s);
                            """,
                            (pid, page_val, datetime.utcnow()),
                        )
                    else:
                        if isinstance(entry, dict):
                            url_val = entry.get("url") or entry.get("Url") or ""
                            method_val = (entry.get("Method") or entry.get("method") or "GET").upper()
                            type_val = type_val_raw or "ROLE"
                        else:
                            url_val = str(entry)
                            method_val = "GET"
                            type_val = "ROLE"
                        if not url_val:
                            continue
                        cur.execute(
                            """
                            INSERT INTO url_permissions (permission_id, url, method, type, last_update_datetime)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (pid, url_val, method_val, type_val, datetime.utcnow()),
                        )
            conn.commit()
    except ValueError as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=400)
    except Exception as e:
        conn.rollback()
        return _json_response({"message": str(e), "status": "FAIL"}, status=500)
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/deletePermissionById", methods=["POST"])
def delete_permission():
    data = request.get_json(silent=True) or {}
    pid = data.get("id")
    if not pid:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM url_permissions WHERE permission_id=%s;", (pid,))
            cur.execute("DELETE FROM data_permissions WHERE permission_id=%s;", (pid,))
            cur.execute("DELETE FROM page_permissions WHERE permission_id=%s;", (pid,))
            cur.execute("DELETE FROM permissions WHERE id=%s;", (pid,))
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"status": "OK"})


@rp_bp.route("/getURLbyPermission", methods=["POST"])
def get_url_by_permission():
    data = request.get_json(silent=True) or {}
    pid = data.get("PermissionId")
    if not pid:
        return _json_response({"message": "PermissionId is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, url, method AS "Method", type AS "Type"
                FROM url_permissions
                WHERE permission_id = %s AND UPPER(type) <> 'PAGE'
                UNION ALL
                SELECT id, page AS url, 'GET' AS "Method", 'PAGE' AS "Type"
                FROM page_permissions
                WHERE permission_id = %s;
                """,
                (pid, pid),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getRoleByPermission", methods=["POST"])
def get_role_by_permission():
    data = request.get_json(silent=True) or {}
    pid = data.get("id")
    if not pid:
        return _json_response({"message": "id is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT r.id AS "RoleId", r.code AS "RoleName"
                FROM role_permissions rp
                JOIN roles r ON r.id = rp.role_id
                WHERE rp.permission_id = %s;
                """,
                (pid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getDataPermissionList", methods=["POST"])
def get_data_permission_list():
    # permission_type='DATA'
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    code = data.get("Code")
    offset = (page - 1) * page_size

    where = ["permission_type = 'DATA'"]
    params = []
    if code:
        where.append("code ILIKE %s")
        params.append(f"%{code}%")
    where_sql = "WHERE " + " AND ".join(where)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT COUNT(*) AS count FROM permissions {where_sql};", params)
            total = cur.fetchone()["count"]
            cur.execute(
                f"""
                SELECT id, code AS "Code", permission_type AS "PermissionType",
                       description AS "Description"
                FROM permissions
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

    return _json_response({"data": rows, "total_row": [{"sum": total}], "status": "OK"})


@rp_bp.route("/getRolePermissionList", methods=["POST"])
def get_role_permission_list():
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    code = data.get("Code")
    ptype = data.get("PermissionType") or data.get("PermissionTypes")
    offset = (page - 1) * page_size

    where = []
    params = []
    if ptype:
        if isinstance(ptype, (list, tuple, set)):
            where.append("permission_type = ANY(%s)")
            params.append(list(ptype))
        else:
            where.append("permission_type = %s")
            params.append(ptype)
    else:
        where.append("permission_type = ANY(%s)")
        params.append(["ROLE", "PAGE"])
    if code:
        where.append("code ILIKE %s")
        params.append(f"%{code}%")
    where_sql = "WHERE " + " AND ".join(where)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT COUNT(*) AS count FROM permissions {where_sql};", params)
            total = cur.fetchone()["count"]
            cur.execute(
                f"""
                SELECT id, code AS "Code", permission_type AS "PermissionType",
                       description AS "Description"
                FROM permissions
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

    return _json_response({"data": rows, "total_row": [{"sum": total}], "status": "OK"})


@rp_bp.route("/getURLbyPermissionList", methods=["POST"])
def get_url_by_permission_list():
    """
    Nhận PermissionList (id hoặc code), trả về danh sách url/method/type.
    """
    data = request.get_json(silent=True) or {}
    perms = data.get("PermissionList") or []
    if not perms:
        return _json_response({"data": [], "status": "OK"})

    # tách code và id
    perm_ids = []
    perm_codes = []
    for p in perms:
        try:
            perm_ids.append(int(p))
        except Exception:
            if p is not None:
                perm_codes.append(str(p))

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if perm_ids and perm_codes:
                cur.execute(
                    """
                    SELECT up.url, up.method AS "Method", up.type AS "Type"
                    FROM url_permissions up
                    WHERE UPPER(up.type) <> 'PAGE'
                    JOIN permissions p ON p.id = up.permission_id
                    WHERE p.id = ANY(%s) OR p.code = ANY(%s)
                    UNION ALL
                    SELECT pp.page AS url, 'GET' AS "Method", 'PAGE' AS "Type"
                    FROM page_permissions pp
                    JOIN permissions p ON p.id = pp.permission_id
                    WHERE p.id = ANY(%s) OR p.code = ANY(%s);
                    """,
                    (perm_ids, perm_codes, perm_ids, perm_codes),
                )
            elif perm_ids:
                cur.execute(
                    """
                    SELECT url, method AS "Method", type AS "Type"
                    FROM url_permissions
                    WHERE permission_id = ANY(%s) AND UPPER(type) <> 'PAGE'
                    UNION ALL
                    SELECT page AS url, 'GET' AS "Method", 'PAGE' AS "Type"
                    FROM page_permissions
                    WHERE permission_id = ANY(%s);
                    """,
                    (perm_ids, perm_ids),
                )
            else:
                cur.execute(
                    """
                    SELECT up.url, up.method AS "Method", up.type AS "Type"
                    FROM url_permissions up
                    WHERE UPPER(up.type) <> 'PAGE'
                    JOIN permissions p ON p.id = up.permission_id
                    WHERE p.code = ANY(%s)
                    UNION ALL
                    SELECT pp.page AS url, 'GET' AS "Method", 'PAGE' AS "Type"
                    FROM page_permissions pp
                    JOIN permissions p ON p.id = pp.permission_id
                    WHERE p.code = ANY(%s);
                    """,
                    (perm_codes, perm_codes),
                )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})


@rp_bp.route("/getPageByUser", methods=["POST"])
def get_page_by_user():
    """Return distinct pages a user can access based on roles -> permissions -> page_permissions."""
    data = request.get_json(silent=True) or {}
    uid = data.get("UserId")
    if not uid:
        return _json_response({"message": "UserId is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT pp.page AS "Page", pp.permission_id AS "PermissionId"
                FROM user_roles ur
                JOIN role_permissions rp ON rp.role_id = ur.role_id
                JOIN page_permissions pp ON pp.permission_id = rp.permission_id
                WHERE ur.user_id = %s;
                """,
                (uid,),
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})
