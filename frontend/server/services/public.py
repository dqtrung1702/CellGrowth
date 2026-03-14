from flask import Blueprint, request, jsonify
import requests
from config import Config

public = Blueprint('public_blueprint', __name__)


def _forward(path):
    try:
        resp = requests.get(Config.UAA_URL.rstrip('/') + path, params=request.args, timeout=5)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as exc:
        return jsonify({'status': 'FAIL', 'message': f'Upstream error: {exc}'}), 502


@public.route('/publicRoleList', methods=['GET'])
def public_role_list_proxy():
    return _forward('/publicRoleList')


@public.route('/publicPermissionList', methods=['GET'])
def public_permission_list_proxy():
    return _forward('/publicPermissionList')
