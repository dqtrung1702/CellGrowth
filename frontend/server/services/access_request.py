from flask import Blueprint, render_template, request, redirect, url_for, session
import requests
from config import Config
from base import auth_info

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
    type_filter = request.args.get('type')
    page = int(request.args.get('page', 1))
    mine = request.args.get('mine', 'true')
    res = _uaa_get('/access_requests', cookies=cookies, params={
        'status': status,
        'type': type_filter,
        'page': page,
        'page_size': 20,
        'mine': mine
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
    xauth, _ = auth_info(jwt_token)
    if not xauth:
        return redirect(url_for('auth_blueprint.login'))

    if request.method == 'POST':
        action = request.form.get('action')
        note = request.form.get('note')
        if action == 'approve':
            res = _uaa_post(f'/access_requests/{req_id}/approve', cookies=cookies, payload={'Note': note})
        elif action == 'reject':
            res = _uaa_post(f'/access_requests/{req_id}/reject', cookies=cookies, payload={'Note': note})
        elif action == 'cancel':
            res = _uaa_post(f'/access_requests/{req_id}/cancel', cookies=cookies, payload={})
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
    return render_template('access_request_detail.html', title='Request Detail', auth=True, req=req_data)
