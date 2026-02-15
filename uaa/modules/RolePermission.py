from flask import Blueprint, request
from werkzeug.wrappers import Response
import json
from psycopg2.extras import RealDictCursor
from bson import json_util
from datetime import datetime

from models.database import db

rp_bp = Blueprint("role_permission_api", __name__)
_db = db()


def _json_response(payload, status=200):
    return Response(json.dumps(payload, default=json_util.default), mimetype="application/json", status=status)


def _ensure_set(cur, set_entry):
    """Insert set if not exists, return set_id."""
    setname = set_entry.get("setname") or set_entry.get("SetName") or set_entry.get("name") or "default"
    settbl = set_entry.get("settbl") or set_entry.get("SetTbl") or set_entry.get("table") or "*"
    setcol = set_entry.get("setcol") or set_entry.get("SetCol") or set_entry.get("column") or "*"
    setval = set_entry.get("setval") or set_entry.get("SetVal") or set_entry.get("value") or "*"
    cur.execute(
        """
        INSERT INTO sets (setname, settbl, setcol, setval)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (setname, settbl, setcol, setval) DO UPDATE SET setname=EXCLUDED.setname
        RETURNING id;
        """,
        (setname, settbl, setcol, setval),
    )
    return cur.fetchone()[0]


@rp_bp.route("/getRoleList", methods=["POST"])
def get_role_list():
    data = request.get_json(silent=True) or {}
    page = int(data.get("page", 1))
    page_size = int(data.get("page_size", 10))
    code = data.get("Code")
    offset = (page - 1) * page_size

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if code:
                cur.execute("SELECT COUNT(*) AS count FROM roles WHERE code ILIKE %s;", (f"%{code}%",))
                total = cur.fetchone()["count"]
                cur.execute(
                    """
                    SELECT id, code AS "Code", description AS "Description",
                           last_update_username AS "LastUpdateUserName",
                           last_update_datetime AS "LastUpdateDateTime"
                    FROM roles
                    WHERE code ILIKE %s
                    ORDER BY id
                    LIMIT %s OFFSET %s;
                    """,
                    (f"%{code}%", page_size, offset),
                )
            else:
                cur.execute("SELECT COUNT(*) AS count FROM roles;")
                total = cur.fetchone()["count"]
                cur.execute(
                    """
                    SELECT id, code AS "Code", description AS "Description",
                           last_update_username AS "LastUpdateUserName",
                           last_update_datetime AS "LastUpdateDateTime"
                    FROM roles
                    ORDER BY id
                    LIMIT %s OFFSET %s;
                    """,
                    (page_size, offset),
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

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, code AS "Code", description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM roles WHERE id = %s;
                """,
                (role_id,),
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
    ptype = data.get("PermissionType")
    offset = (page - 1) * page_size

    where = []
    params = []
    if code:
        where.append("code ILIKE %s")
        params.append(f"%{code}%")
    if ptype:
        where.append("permission_type = %s")
        params.append(ptype)
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

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, code AS "id", code AS "PermissionName",
                       permission_type AS "PermissionType",
                       description AS "Description",
                       last_update_username AS "LastUpdateUserName",
                       last_update_datetime AS "LastUpdateDateTime"
                FROM permissions
                WHERE id = ANY(%s);
                """,
                (ids_int,),
            )
            rows = cur.fetchall()
            # attach DataSets if DATA type
            cur.execute(
                """
                SELECT dp.permission_id, s.id, s.setname, s.settbl, s.setcol, s.setval
                FROM data_permissions dp
                JOIN sets s ON s.id = dp.set_id
                WHERE dp.permission_id = ANY(%s);
                """,
                (ids_int,),
            )
            data_sets = cur.fetchall()
            if data_sets:
                # map by permission_id
                by_pid = {}
                for r in data_sets:
                    by_pid.setdefault(r[0], []).append(
                        {
                            "SetId": r[1],
                            "SetName": r[2],
                            "SetTbl": r[3],
                            "SetCol": r[4],
                            "SetVal": r[5],
                        }
                    )
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
    ptype = data.get("PermissionType")
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
                    set_id = _ensure_set(cur, ds if isinstance(ds, dict) else {})
                    cur.execute(
                        """
                        INSERT INTO data_permissions (permission_id, set_id, last_update_datetime)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (permission_id, set_id) DO NOTHING;
                        """,
                        (pid, set_id, datetime.utcnow()),
                    )
            else:
                for url_entry in url_list:
                    if isinstance(url_entry, dict):
                        url_val = url_entry.get("url") or url_entry.get("Url") or ""
                        method_val = (url_entry.get("Method") or url_entry.get("method") or "GET").upper()
                        type_val = url_entry.get("Type") or ptype or "ROLE"
                    else:
                        url_val = str(url_entry)
                        method_val = "GET"
                        type_val = ptype
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
    ptype = data.get("PermissionType")
    url_list = data.get("UrlList") or []
    data_sets = data.get("DataSets") or []

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor() as cur:
            # fetch current permission_type if not provided
            if ptype is None:
                cur.execute("SELECT permission_type FROM permissions WHERE id=%s;", (pid,))
                row = cur.fetchone()
                ptype = row[0] if row else "ROLE"
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
            # reset url or data list
            cur.execute("DELETE FROM url_permissions WHERE permission_id=%s;", (pid,))
            cur.execute("DELETE FROM data_permissions WHERE permission_id=%s;", (pid,))
            if ptype == "DATA":
                for ds in data_sets:
                    set_id = _ensure_set(cur, ds if isinstance(ds, dict) else {})
                    cur.execute(
                        """
                        INSERT INTO data_permissions (permission_id, set_id, last_update_datetime)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (permission_id, set_id) DO NOTHING;
                        """,
                        (pid, set_id, datetime.utcnow()),
                    )
            else:
                for url_entry in url_list:
                    if isinstance(url_entry, dict):
                        url_val = url_entry.get("url") or url_entry.get("Url") or ""
                        method_val = (url_entry.get("Method") or url_entry.get("method") or "GET").upper()
                        type_val = url_entry.get("Type") or ptype or "ROLE"
                    else:
                        url_val = str(url_entry)
                        method_val = "GET"
                        type_val = ptype or "ROLE"
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
                WHERE permission_id = %s;
                """,
                (pid,),
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
    offset = (page - 1) * page_size

    where = ["permission_type = 'ROLE'"]
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
                    JOIN permissions p ON p.id = up.permission_id
                    WHERE p.id = ANY(%s) OR p.code = ANY(%s);
                    """,
                    (perm_ids, perm_codes),
                )
            elif perm_ids:
                cur.execute(
                    """
                    SELECT up.url, up.method AS "Method", up.type AS "Type"
                    FROM url_permissions up
                    WHERE up.permission_id = ANY(%s);
                    """,
                    (perm_ids,),
                )
            else:
                cur.execute(
                    """
                    SELECT up.url, up.method AS "Method", up.type AS "Type"
                    FROM url_permissions up
                    JOIN permissions p ON p.id = up.permission_id
                    WHERE p.code = ANY(%s);
                    """,
                    (perm_codes,),
                )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json_response({"data": rows, "status": "OK"})
