from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from config import Config
from base import auth_info, _menu_flags_from_session

access_request = Blueprint('access_request_blueprint', __name__)


def _uaa_get(path, cookies=None, params=None):
    return requests.get(Config.UAA_URL + path, params=params or {}, cookies=cookies, timeout=5)


def _uaa_post(path, cookies=None, payload=None):
    return requests.post(Config.UAA_URL + path, json=payload or {}, cookies=cookies, timeout=5)


@access_request.route('/access_requests')
def access_request_list():
    cookies = request.cookies
    jwt_token = cookies.get('app_token','')  
    xauth, _ = auth_info(jwt_token)
    if not xauth:
        return redirect(url_for('auth_blueprint.login'))
    status = request.args.get('status')
    requester = request.args.get('requester')
    created_from = request.args.get('created_from')
    created_to = request.args.get('created_to')
    page = int(request.args.get('page', 1))
    res = _uaa_get('/access_requests', cookies=cookies, params={
        'status': status,
        'requester': requester,
        'created_from': created_from,
        'created_to': created_to,
        'page': page,
        'page_size': 20
    })
    data = res.json() if res.content else {}
    requests_rows = data.get('data', []) if res.status_code == 200 else []
    total = data.get('total', 0)
    return render_template('access_requests.html', title='Access Requests', auth=True,
                           requests=requests_rows, total=total, page=page)


@access_request.route('/access_requests/<int:req_id>', methods=['GET', 'POST'])
def access_request_detail(req_id):
    cookies = request.cookies
    jwt_token = cookies.get('app_token','')
    xauth, info = auth_info(jwt_token)
    if not xauth:
        return redirect(url_for('auth_blueprint.login'))

    # Operator UI: dựa trên menu flags (đã tính từ permissions/pages) và không phải người request
    flags = _menu_flags_from_session()
    is_operator = bool(flags.get("AccessRequests") and (flags.get("Permissions") or flags.get("Roles")))

    if request.method == 'POST':
        action = request.form.get('action')
        note = request.form.get('note')
        if action == 'approve':
            res = _uaa_post(f'/access_requests/{req_id}/approve', cookies=cookies, payload={'Note': note})
        elif action == 'reject':
            res = _uaa_post(f'/access_requests/{req_id}/reject', cookies=cookies, payload={'Note': note})
        elif action == 'cancel':
            res = _uaa_post(f'/access_requests/{req_id}/cancel', cookies=cookies, payload={})
        elif action == 'update':
            roles_raw = request.form.getlist('roles') or request.form.get('roles', '').split(',')
            dps_raw = request.form.getlist('data_perms') or request.form.get('data_perms', '').split(',')

            def _parse_ids(values):
                # No selection at all -> None (giữ nguyên items)
                if not values or all(not str(v).strip() for v in values):
                    return None
                ints = []
                for v in values:
                    v_str = str(v).strip()
                    if not v_str:
                        continue
                    if v_str.isdigit():
                        ints.append(int(v_str))
                return ints

            roles = _parse_ids(roles_raw)
            dps = _parse_ids(dps_raw)

            payload = {'Reason': note}
            if roles is not None:
                payload['Roles'] = roles
            if dps is not None:
                payload['DataPermissions'] = dps
            res = _uaa_post(f'/access_requests/{req_id}/update', cookies=cookies, payload=payload)
        else:
            res = None
        if res is not None and res.status_code == 403:
            return redirect('Accessisdenied')
        if res is not None and res.status_code == 401:
            return redirect(url_for('auth_blueprint.login'))
        return redirect(url_for('access_request_blueprint.access_request_detail', req_id=req_id))

    res = _uaa_get(f'/access_requests/{req_id}', cookies=cookies)
    if res.status_code == 403:
        return redirect('Accessisdenied')
    if res.status_code == 401:
        return redirect(url_for('auth_blueprint.login'))
    data = res.json() if res.content else {}
    req_data = data.get('data', {}) if res.status_code == 200 else {}
    is_owner = req_data.get("requester_id") == info.get("UserId")
    items = req_data.get("Items") or []
    role_items = []
    data_perm_items = []
    for it in items:
        if it.get("role_id"):
            role_items.append({"id": it.get("role_id"), "text": it.get("role_code") or str(it.get("role_id"))})
        if it.get("data_permission_id"):
            data_perm_items.append({"id": it.get("data_permission_id"), "text": it.get("data_permission_code") or str(it.get("data_permission_id"))})
    if is_operator and not is_owner:
        tmpl = 'access_request_operator.html'
    elif is_owner:
        tmpl = 'access_request_requester.html'
    else:
        tmpl = 'access_request_requester.html'  # fallback view only (no actions)

    return render_template(
        tmpl,
        title='Request Detail',
        auth=True,
        req=req_data,
        me=info.get("UserId"),
        role_items=role_items,
        data_perm_items=data_perm_items,
    )
