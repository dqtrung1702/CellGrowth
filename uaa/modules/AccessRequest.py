from flask import Blueprint, request
from werkzeug.wrappers import Response
import json
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import jwt
import re

from config import Config
from models.database import db

ar_bp = Blueprint("access_request_api", __name__)
_db = db()


def _json(payload, status=200):
    return Response(json.dumps(payload, default=str), mimetype="application/json", status=status)


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


def _get_username(user_id):
    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT username FROM users WHERE id=%s;", (user_id,))
            row = cur.fetchone()
            return row.get("username") if row else None
    finally:
        _db.conn_pool.putconn(conn)


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
    for col, val in filters:
        clauses.append(f"{col} = %s")
        params.append(val)
    return "(" + " OR ".join(clauses) + ")", params


def _add_log(cur, req_id, actor_id, action, note=None):
    cur.execute(
        """
        INSERT INTO access_request_logs (request_id, actor_id, action, note, created_at)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (req_id, actor_id, action, note, datetime.utcnow()),
    )


@ar_bp.route("/access_requests", methods=["POST"])
def create_request():
    data = request.get_json(silent=True) or {}
    user_id = _current_user_id()
    if not user_id:
        return _json({"message": "Unauthorized", "status": "FAIL"}, status=401)

    req_type = (data.get("Type") or data.get("request_type") or "ROLE").upper()
    if req_type not in ("ROLE", "DATA"):
        return _json({"message": "Type must be ROLE or DATA", "status": "FAIL"}, status=400)

    roles = data.get("Roles") or data.get("roles") or []
    data_perms = data.get("DataPermissions") or data.get("data_permissions") or []
    set_ids = data.get("SetIds") or data.get("set_ids") or []
    reason = data.get("Reason") or data.get("reason")
    ttl_hours = data.get("TtlHours") or data.get("ttl_hours")

    if not roles and not data_perms and not set_ids:
        return _json({"message": "At least one role or data scope is required", "status": "FAIL"}, status=400)

    requester_username = _get_username(user_id)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO access_requests (requester_id, requester, request_type, status, reason, ttl_hours, created_at, updated_at)
                VALUES (%s, %s, %s, 'SUBMITTED', %s, %s, %s, %s)
                RETURNING id;
                """,
                (user_id, requester_username, req_type, reason, ttl_hours, datetime.utcnow(), datetime.utcnow()),
            )
            req_id = cur.fetchone()["id"]

            for rid in roles:
                cur.execute(
                    """
                    INSERT INTO access_request_items (request_id, role_id, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (req_id, rid, datetime.utcnow()),
                )
            for dp in data_perms:
                cur.execute(
                    """
                    INSERT INTO access_request_items (request_id, data_permission_id, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (req_id, dp, datetime.utcnow()),
                )
            for sid in set_ids:
                cur.execute(
                    """
                    INSERT INTO access_request_items (request_id, set_id, created_at)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (req_id, sid, datetime.utcnow()),
                )
            _add_log(cur, req_id, user_id, "SUBMIT", note=reason)
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json({"data": {"RequestId": req_id}, "status": "OK"}, status=200)


@ar_bp.route("/access_requests", methods=["GET"])
def list_requests():
    user_id = _current_user_id()
    if not user_id:
        return _json({"message": "Unauthorized", "status": "FAIL"}, status=401)

    status_filter = request.args.get("status")
    type_filter = request.args.get("type")
    mine_only = request.args.get("mine", "true").lower() != "false"  # default: only own
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    offset = (page - 1) * page_size
    scope_sql, scope_params = _data_scope_filters(user_id, table_name="access_requests")
    full_access = scope_sql is None and scope_params is None

    # Nếu user có full DATA scope hoặc có scope hợp lệ (khác \"1=0\") cho access_requests
    # thì cho phép xem theo scope (không ép mine=true).
    if full_access or (scope_sql and scope_sql != "1=0"):
        mine_only = False

    where = []
    params = []
    if mine_only:
        where.append("requester_id = %s")
        params.append(user_id)
    if status_filter:
        where.append("status = %s")
        params.append(status_filter.upper())
    if type_filter:
        where.append("request_type = %s")
        params.append(type_filter.upper())
    # Chỉ áp dụng data scope khi xem không chỉ của chính mình và scope không phải deny-all
    if not mine_only and scope_sql and scope_sql != "1=0":
        where.append(scope_sql)
        params.extend(scope_params)
    where_sql = "WHERE " + " AND ".join(where) if where else ""

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT COUNT(*) AS count FROM access_requests {where_sql};", params)
            total = cur.fetchone()["count"]
            cur.execute(
                f"""
                SELECT ar.id,
                       ar.requester_id,
                       ar.requester AS requester_username,
                       ar.request_type,
                       ar.status,
                       ar.reason,
                       ar.ttl_hours,
                       ar.created_at,
                       ar.updated_at,
                       ar.approved_by,
                       ar.approved_at
                FROM access_requests ar
                LEFT JOIN users u ON u.id = ar.requester_id
                {where_sql}
                ORDER BY ar.created_at DESC
                LIMIT %s OFFSET %s;
                """,
                params + [page_size, offset],
            )
            rows = cur.fetchall()
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json({"data": rows, "total": total, "status": "OK"})


@ar_bp.route("/access_requests/<int:req_id>", methods=["GET"])
def get_request(req_id):
    user_id = _current_user_id()
    if not user_id:
        return _json({"message": "Unauthorized", "status": "FAIL"}, status=401)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT ar.*,
                       u.username AS requester_username
                FROM access_requests ar
                LEFT JOIN users u ON u.id = ar.requester_id
                WHERE ar.id=%s;
                """,
                (req_id,),
            )
            req_row = cur.fetchone()
            if not req_row:
                return _json({"message": "Not found", "status": "FAIL"}, status=404)
            # Nếu không phải requester thì kiểm tra data scope
            if req_row.get("requester_id") != user_id:
                scope_sql, scope_params = _data_scope_filters(user_id, table_name="access_requests")
                if scope_sql:
                    cur.execute(
                        f"SELECT 1 FROM access_requests WHERE id=%s AND {scope_sql};",
                        [req_id] + scope_params,
                    )
                    ok = cur.fetchone()
                    if not ok:
                        return _json({"message": "Access denied", "status": "FAIL"}, status=403)

            cur.execute(
                """
                SELECT id, role_id, data_permission_id, set_id, note
                FROM access_request_items WHERE request_id=%s ORDER BY id;
                """,
                (req_id,),
            )
            items = cur.fetchall()
            cur.execute(
                """
                SELECT l.id,
                       l.actor_id,
                       u.username AS actor_username,
                       l.action,
                       l.note,
                       l.created_at
                FROM access_request_logs l
                LEFT JOIN users u ON u.id = l.actor_id
                WHERE l.request_id=%s
                ORDER BY l.created_at ASC;
                """,
                (req_id,),
            )
            logs = cur.fetchall()
    finally:
        _db.conn_pool.putconn(conn)

    req_row["Items"] = items
    req_row["Logs"] = logs
    return _json({"data": req_row, "status": "OK"})


def _apply_request(cur, req_row, items):
    actions = []
    target_user = req_row["requester_id"]
    # Apply roles
    role_ids = [it.get("role_id") for it in items if it.get("role_id")]
    for rid in role_ids:
        cur.execute(
            """
            INSERT INTO user_roles (user_id, role_id, last_update_datetime)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, role_id) DO NOTHING;
            """,
            (target_user, rid, datetime.utcnow()),
        )
        actions.append({"role_id": rid, "action": "added"})

    # Apply data permission: take first data_permission_id if provided
    data_perm_ids = [it.get("data_permission_id") for it in items if it.get("data_permission_id")]
    if data_perm_ids:
        cur.execute(
            """
            UPDATE users SET data_permission_id = %s, updated_at=%s WHERE id=%s;
            """,
            (data_perm_ids[0], datetime.utcnow(), target_user),
        )
        actions.append({"data_permission_id": data_perm_ids[0], "action": "set"})

    return actions


@ar_bp.route("/access_requests/<int:req_id>/approve", methods=["POST"])
def approve_request(req_id):
    user_id = _current_user_id()
    if not user_id:
        return _json({"message": "Unauthorized", "status": "FAIL"}, status=401)

    note = (request.get_json(silent=True) or {}).get("Note")

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM access_requests WHERE id=%s FOR UPDATE;", (req_id,))
            req_row = cur.fetchone()
            if not req_row:
                return _json({"message": "Not found", "status": "FAIL"}, status=404)
            if req_row.get("status") != "SUBMITTED":
                return _json({"message": "Request not in SUBMITTED", "status": "FAIL"}, status=400)

            cur.execute("SELECT * FROM access_request_items WHERE request_id=%s;", (req_id,))
            items = cur.fetchall()

            actions = _apply_request(cur, req_row, items)

            cur.execute(
                """
                UPDATE access_requests
                SET status='APPROVED', approved_by=%s, approved_at=%s, updated_at=%s, apply_result_json=%s
                WHERE id=%s;
                """,
                (user_id, datetime.utcnow(), datetime.utcnow(), json.dumps(actions), req_id),
            )
            _add_log(cur, req_id, user_id, "APPROVE", note=note)
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json({"status": "OK", "actions": actions})


@ar_bp.route("/access_requests/<int:req_id>/reject", methods=["POST"])
def reject_request(req_id):
    user_id = _current_user_id()
    if not user_id:
        return _json({"message": "Unauthorized", "status": "FAIL"}, status=401)

    payload = request.get_json(silent=True) or {}
    note = payload.get("Note") or payload.get("Reason")
    if not note:
        return _json({"message": "Reject note is required", "status": "FAIL"}, status=400)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM access_requests WHERE id=%s FOR UPDATE;", (req_id,))
            req_row = cur.fetchone()
            if not req_row:
                return _json({"message": "Not found", "status": "FAIL"}, status=404)
            if req_row.get("status") != "SUBMITTED":
                return _json({"message": "Request not in SUBMITTED", "status": "FAIL"}, status=400)

            cur.execute(
                """
                UPDATE access_requests
                SET status='REJECTED', rejected_reason=%s, updated_at=%s
                WHERE id=%s;
                """,
                (note, datetime.utcnow(), req_id),
            )
            _add_log(cur, req_id, user_id, "REJECT", note=note)
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json({"status": "OK"})


@ar_bp.route("/access_requests/<int:req_id>/cancel", methods=["POST"])
def cancel_request(req_id):
    user_id = _current_user_id()
    if not user_id:
        return _json({"message": "Unauthorized", "status": "FAIL"}, status=401)

    conn = _db.conn_pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM access_requests WHERE id=%s FOR UPDATE;", (req_id,))
            req_row = cur.fetchone()
            if not req_row:
                return _json({"message": "Not found", "status": "FAIL"}, status=404)
            if req_row.get("requester_id") != user_id:
                return _json({"message": "Forbidden", "status": "FAIL"}, status=403)
            if req_row.get("status") != "SUBMITTED":
                return _json({"message": "Request not in SUBMITTED", "status": "FAIL"}, status=400)

            cur.execute(
                """
                UPDATE access_requests
                SET status='CANCELLED', updated_at=%s
                WHERE id=%s;
                """,
                (datetime.utcnow(), req_id),
            )
            _add_log(cur, req_id, user_id, "CANCEL")
            conn.commit()
    finally:
        _db.conn_pool.putconn(conn)

    return _json({"status": "OK"})
