import base64
import json
import sys
import requests
from flask import request, redirect, url_for, render_template
from config import Config
from base import require_page_access

from . import permission, _fmt_dt, _date_key


@permission.route('/SsoTs', methods=['GET', 'POST'])
def SsoTs():
    base64_template = request.values.get('template')
    base64_bytes = base64_template.encode('utf-8')
    template_bytes = base64.b64decode(base64_bytes)
    template = template_bytes.decode('utf-8')
    return template


@permission.route('/Permission', methods=['GET'])
@require_page_access
def Permission():
    cookies = request.cookies
    url = Config.UAA_URL
    page_size = Config.PAGE_SIZE
    data = {'page_size': page_size, 'PermissionType': ['ROLE', 'DATA']}
    isSearch = False
    if request.args.get('data'):
        data.update(json.loads(request.args.get('data')))
        page = data.get('page')
        isSearch = True
    else:
        page = request.args.get('page', type=int, default=1)
        data.update({'page': page})
    res = requests.post(url + '/getPermissionList', json=data, cookies=cookies, timeout=5)
    if res.status_code != 200:
        return redirect('home')
    if res.json().get('status', '') != 'OK':
        if res.status_code == 403:
            return redirect('Accessisdenied')
        return redirect('home')

    rows = res.json().get('data') or []
    total_raw = res.json().get('total_row') or []
    total_row = int(total_raw[0].get('sum')) if total_raw and total_raw[0].get('sum') else 0
    permissions = []
    for pos, line in enumerate(rows):
        permissions.append({
            "id": line.get('id'),
            "STT": pos + 1,
            "PermissionName": line.get('Code'),
            "PermissionType": line.get('PermissionType'),
            "Description": line.get('Description'),
            "LastUpdateDateTime": _fmt_dt(line.get('LastUpdateDateTime'))
        })
    total_pages = (round(total_row / page_size) + 1 if round(total_row / page_size) < (total_row / page_size) else round(total_row / page_size)) if page_size else 1
    pagination = {'page': page, 'total_pages': total_pages}
    if isSearch:
        return {'permissions': permissions, 'pagination': pagination}
    template = render_template('permission.html', title='Role', auth=True, permissions=permissions, pagination=pagination)
    return template


@permission.route('/permission_detail', methods=['GET', 'POST'])
@require_page_access
def permission_detail():
    cookies = request.cookies
    url = Config.UAA_URL
    incoming = request.values
    PermissionId = incoming.get('id') or "New"
    if request.method == 'POST':
        # pull all request values before we start building the payload
        PermissionType = incoming.get('PermissionType', 'ROLE')
        PermissionType = 'DATA' if PermissionType == 'DATA' else 'ROLE'
        Description = incoming.get('Description', None)
        PermissionName = incoming.get('PermissionName', None)
        UrlListJSON = incoming.get('UrlListJSON')
        DataSetsJSON = incoming.get('DataSetsJSON')
        UrlList = []
        DataSets = []
        if UrlListJSON:
            try:
                UrlList = json.loads(UrlListJSON)
            except Exception:
                UrlList = []
        if DataSetsJSON:
            try:
                if DataSetsJSON != "__UNCHANGED__":
                    DataSets = json.loads(DataSetsJSON)
            except Exception:
                DataSets = []
        payload = {'Description': Description, 'PermissionType': PermissionType, 'UrlList': UrlList}
        if DataSetsJSON != "__UNCHANGED__":
            payload.update({'DataSets': DataSets})
        if PermissionId != "New":
            payload.update({'PermissionId': PermissionId})
            res = requests.post(url + '/updatePermission', json=payload, cookies=cookies, timeout=5)
        else:
            payload.update({'Code': PermissionName})
            res = requests.post(url + '/addPermission', json=payload, cookies=cookies, timeout=5)

        if res.status_code != 200:
            try:
                return res.json(), res.status_code
            except Exception:
                return res.text, res.status_code
        if res.json().get('status', '') == 'OK':
            data = res.json().get('data') or {}
            target_id = PermissionId if PermissionId != "New" else (data.get('id') if isinstance(data, dict) else None)
            if target_id:
                return redirect(url_for('permission_blueprint.permission_detail', id=target_id))
            return redirect('Permission')
        elif res.status_code == 403:
            return redirect('Accessisdenied')
        else:
            return redirect('home')

    # GET flow
    permission_data = {}
    urlpermission = []
    sets = []
    try:
        res_sets = requests.post(url + '/getSetList', json={}, cookies=cookies, timeout=5)
        if res_sets.status_code == 200 and res_sets.json().get('status') == 'OK':
            sets = res_sets.json().get('data', [])
    except Exception:
        sets = []
    if PermissionId != 'New':
        # permission info
        res = requests.post(url + '/getPermissionInfo', json={'ids': [PermissionId]}, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status', '') == 'OK':
            data = res.json().get('data')
            permission_data = (data or [{}])[0]
            permission_data['LastUpdateDateTime'] = _fmt_dt(permission_data.get('LastUpdateDateTime'))
            permission_data['PermissionType'] = 'DATA' if permission_data.get('PermissionType') == 'DATA' else 'ROLE'
        elif res.status_code == 403:
            return redirect('Accessisdenied')
        else:
            return redirect('home')
        # urls/pages
        res = requests.post(url + '/getURLbyPermission', json={'PermissionId': PermissionId}, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status', '') == 'OK':
            data = res.json().get('data')
            for pos, line in enumerate(data):
                linedata = {"STT": pos + 1}
                linedata.update(line)
                urlpermission.append(linedata)
        elif res.status_code == 403:
            return redirect('Accessisdenied')
        else:
            return redirect('home')

    return render_template('permissiondetail.html',
                           title='Permission',
                           auth=True,
                           permission=permission_data,
                           urlpermission=urlpermission,
                           sets=sets)


@permission.route('/permission_searching', methods=['GET', 'POST'])
@require_page_access
def permission_searching():
    # Return JSON so AJAX on UI works for all filters
    cookies = request.cookies
    url = Config.UAA_URL
    ui_page_size = Config.PAGE_SIZE
    payload = {}
    try:
        payload.update(json.loads(request.data.decode('utf-8')))
    except Exception:
        pass
    page = int(payload.get('page', 1) or 1)
    code_filter = payload.get('Code')
    ptype_filter = payload.get('PermissionType')
    desc_filter = (payload.get('Description') or '').lower()
    date_filter = (payload.get('LastUpdateDateTime') or '').strip()
    date_filter_key = _date_key(date_filter) if date_filter else None
    print("[permission_searching] input", json.dumps(payload), "date_key", date_filter_key, file=sys.stderr)

    # fetch all pages (batch) then filter locally on Description/Date
    all_rows = []
    page_fetch = 1
    page_size_fetch = 500
    while True:
        fetch_payload = {
            'page': page_fetch,
            'page_size': page_size_fetch,
            'Code': code_filter,
            'PermissionType': ptype_filter
        }
        res = requests.post(url + '/getPermissionList', json=fetch_payload, cookies=cookies, timeout=5)
        if not (res.status_code == 200 and res.json().get('status') == 'OK'):
            break
        batch = res.json().get('data', [])
        all_rows.extend(batch)
        if len(batch) < page_size_fetch or page_fetch >= 20:  # safety cap
            break
        page_fetch += 1
    if all_rows:
        filtered = []
        for line in all_rows:
            desc = (line.get('Description') or '').lower()
            last = (line.get('LastUpdateDateTime') or '')
            last_key = _date_key(last)
            if desc_filter and desc_filter not in desc:
                continue
            if date_filter_key:
                # compare normalized date; also allow original string startswith to be safe
                if date_filter_key != last_key and date_filter not in _fmt_dt(last):
                    continue
            elif date_filter and date_filter not in last:
                continue
            filtered.append(line)
        total_row = len(filtered)
        start = (page - 1) * ui_page_size
        end = start + ui_page_size
        page_items = filtered[start:end]
        permissions = []
        for pos, line in enumerate(page_items, start=1 + start):
            permissions.append({
                "id": line.get('id'),
                "STT": pos,
                "PermissionName": line.get('Code'),
                "PermissionType": line.get('PermissionType'),
                "Description": line.get('Description'),
                "LastUpdateDateTime": _fmt_dt(line.get('LastUpdateDateTime'))
            })
        total_pages = int((total_row + ui_page_size - 1) / ui_page_size) or 1
        pagination = {'page': page, 'total_pages': total_pages}
        return {'permissions': permissions, 'pagination': pagination}
    return {'permissions': [], 'pagination': {'page': 1, 'total_pages': 1}, 'status': 'FAIL'}


@permission.route('/permission_deletion', methods=['GET', 'POST'])
@require_page_access
def permission_deletion():
    cookies = request.cookies
    url = Config.UAA_URL
    data = request.values
    PermissionId = data.get('id')
    data = {'id': PermissionId}
    requests.post(url + '/deletePermissionById', json=data, cookies=cookies, timeout=5)
    return redirect(url_for('permission_blueprint.Permission'))


@permission.route('/getRolePermissionList', methods=['POST'])
@require_page_access
def getRolePermissionList():
    cookies = request.cookies
    url = Config.UAA_URL
    data = request.get_json(silent=True) or {}
    page = data.get('page', 1)
    Code = data.get('Code')
    data = {'Code': Code, 'PermissionType': ['ROLE', 'PAGE'], 'page': page, 'page_size': Config.PAGE_SIZE}
    res = requests.post(url + '/getRolePermissionList', json=data, cookies=cookies, timeout=5)
    if res.status_code == 200:
        if res.json().get('status', '') == 'OK':
            data = res.json().get('data')
            permissions = []
            for d in data:
                permissions.append({"id": d.get("id"), "text": d.get("Code")})
            permissions = list({v['id']: v for v in permissions}.values())
            return json.dumps(permissions)


@permission.route('/getURLbyPermission', methods=['GET', 'POST'])
@require_page_access
def getURLbyPermission():
    cookies = request.cookies
    url = Config.UAA_URL
    incoming = request.get_json(silent=True) or {}
    PermissionId = incoming.get('PermissionId') or request.values.get('PermissionId')
    if not PermissionId:
        return {"message": "PermissionId is required"}, 400
    data = {'PermissionId': PermissionId}
    res = requests.post(url + '/getURLbyPermission', json=data, cookies=cookies, timeout=5)
    if res.status_code == 200:
        if res.json().get('status', '') == 'OK':
            data = res.json().get('data')
            urlpermission = []
            for pos, line in enumerate(data):
                linedata = {"STT": pos + 1}
                linedata.update(line)
                urlpermission.append(linedata)
            return json.dumps(urlpermission)
    elif res.status_code == 403:
        return redirect('Accessisdenied')
    else:
        return redirect('home')
