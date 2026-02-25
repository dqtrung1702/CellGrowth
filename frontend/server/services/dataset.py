from flask import Blueprint, request, redirect, render_template, url_for
import requests
import json

from config import Config
from base import auth, require_page_access, attach_csrf_cookie, csrf_protect

dataset = Blueprint(
    'dataset_blueprint',
    __name__,
)


@dataset.route('/datasets', methods=['GET'])
@require_page_access
def datasets():
    """List sets for DATA permissions; filter by header; actions: edit info, manage datasets."""
    cookies = request.cookies
    url = Config.UAA_URL
    page_size = Config.PAGE_SIZE
    jwt_token = cookies.get('app_token','')
    xauth = auth(jwt_token)
    if not xauth:
        return redirect('Accessisdenied')

    # paging
    page = request.args.get('page', type=int, default=1) or 1
    if page < 1:
        page = 1

    # filters (GET)
    payload = {}
    if request.args.get('SetName'):
        payload['SetName'] = request.args.get('SetName')
    if request.args.get('Services'):
        payload['Services'] = request.args.get('Services')
    if request.args.get('SetCode'):
        payload['SetCode'] = request.args.get('SetCode')

    sets = []
    try:
        res = requests.post(url+'/getSetList', json=payload, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status') == 'OK':
            sets = res.json().get('data', [])
    except Exception:
        sets = []

    total_row = len(sets)
    total_pages = int((total_row + page_size - 1) / page_size) if total_row else 0
    if total_pages and page > total_pages:
        page = total_pages

    start = (page - 1) * page_size
    end = start + page_size
    paged_sets = []
    for idx, s in enumerate(sets[start:end]):
        paged_sets.append({
            "SetId": s.get('SetId'),
            "SetName": s.get('SetName'),
            "Services": s.get('Services'),
            "SetCode": s.get('SetCode'),
            "STT": start + idx + 1
        })

    return render_template('dataset.html',
                           title='Data Sets',
                           auth=True,
                           sets=paged_sets,
                           pagination={'page': page, 'total_pages': total_pages} if total_pages else None)


@dataset.route('/dataset_detail', methods=['GET', 'POST'])
@require_page_access
def dataset_detail():
    """Edit datasets rows for a specific set."""
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')
    xauth = auth(jwt_token)
    if not xauth:
        return redirect('Accessisdenied')

    set_id = request.values.get('SetId')
    if not set_id:
        return redirect(url_for('dataset_blueprint.datasets'))

    # load set info
    set_info = {}
    try:
        res = requests.post(url+'/getSetList', json={}, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status') == 'OK':
            for s in res.json().get('data', []):
                if str(s.get("SetId")) == str(set_id):
                    set_info = s
                    break
    except Exception:
        pass

    # handle save datasets
    if request.method == 'POST':
        data_json = request.values.get('DataJSON') or '[]'
        try:
            data_rows = json.loads(data_json)
        except Exception:
            data_rows = []
        payload = {'SetId': set_id, 'Data': data_rows}
        res = requests.post(url+'/updateDatasetBySet', json=payload, cookies=cookies, timeout=5)
        if res.status_code != 200 or res.json().get('status') != 'OK':
            try:
                return res.json(), res.status_code
            except Exception:
                return res.text, res.status_code

    # load current datasets
    datasets = []
    try:
        res = requests.post(url+'/getDatasetBySet', json={'SetId': set_id}, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status') == 'OK':
            datasets = res.json().get('data', [])
    except Exception:
        datasets = []

    return render_template('dataset_detail.html',
                           title='Dataset Detail',
                           auth=True,
                           set_info=set_info,
                           datasets=datasets,
                           SetId=set_id)


@dataset.route('/set_deletion', methods=['GET', 'POST'])
@require_page_access
def set_deletion():
    cookies = request.cookies
    url = Config.UAA_URL
    set_id = request.values.get('SetId') or request.values.get('id')
    if not set_id:
        return redirect(url_for('dataset_blueprint.datasets'))

    res = requests.post(url+'/deleteSetById', json={'SetId': set_id}, cookies=cookies, timeout=5)
    if res.status_code == 403:
        return redirect('Accessisdenied')
    return redirect(url_for('dataset_blueprint.datasets'))


@dataset.route('/set_detail', methods=['GET', 'POST'])
@require_page_access
def set_detail():
    cookies = request.cookies
    url = Config.UAA_URL
    set_id = request.values.get('SetId') or "New"

    if request.method == 'POST':
        setname = request.form.get('SetName') or ''
        services = request.form.get('Services') or ''
        setcode = request.form.get('SetCode') or ''
        if set_id == "New":
            payload = {'SetName': setname, 'Services': services, 'SetCode': setcode}
            res = requests.post(url+'/addSet', json=payload, cookies=cookies, timeout=5)
        else:
            payload = {'SetId': set_id, 'SetName': setname, 'Services': services, 'SetCode': setcode}
            res = requests.post(url+'/updateSet', json=payload, cookies=cookies, timeout=5)
        if res.status_code != 200 or res.json().get('status') != 'OK':
            try:
                err = res.json().get('message','Update failed')
            except Exception:
                err = res.text
            return render_template('set_detail.html',
                                   title='Set Detail',
                                   auth=True,
                                   error=err,
                                   SetId=set_id,
                                   set_info=payload), res.status_code
        # after success, redirect to datasets list
        return redirect(url_for('dataset_blueprint.datasets'))

    # load current set info
    set_info = {}
    if set_id != "New":
        try:
            res = requests.post(url+'/getSetList', json={}, cookies=cookies, timeout=5)
            if res.status_code == 200 and res.json().get('status') == 'OK':
                for s in res.json().get('data', []):
                    if str(s.get("SetId")) == str(set_id):
                        set_info = s
                        break
        except Exception:
            pass

    return render_template('set_detail.html',
                           title='Set Detail',
                           auth=True,
                           SetId=set_id,
                           set_info=set_info)
