import json
import requests
from flask import request
from config import Config
from base import require_page_access

from . import permission


@permission.route('/getDataPermissionList', methods=['POST'])
@require_page_access
def getDataPermissionList():
    cookies = request.cookies
    url = Config.UAA_URL
    data = request.get_json(silent=True) or {}
    page = data.get('page', 1)
    Code = data.get('Code')
    data = {'Code': Code, 'PermissionType': 'DATA', 'page': page, 'page_size': 10}
    res = requests.post(url + '/getDataPermissionList', json=data, cookies=cookies, timeout=5)
    if res.status_code == 200:
        if res.json().get('status', '') == 'OK':
            data = res.json().get('data')
            datapermissions = []
            for d in data:
                datapermissions.append({"id": d.get("id"), "text": d.get("Code")})
            datapermissions = list({v['id']: v for v in datapermissions}.values())
            return json.dumps(datapermissions)
