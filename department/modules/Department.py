from models.database import db
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import requests
import json
from werkzeug.wrappers import Response
from datetime import datetime

route_dept = Blueprint('route_dept', __name__)

@route_dept.before_request
def before_request_func():
    # các request tới route_user đều phải qua đây trước
    cookies = request.cookies
    url = Config.UAA_URL + "check_auth_ext"
    payload={"url":request.url,"method":request.method,"type":'Function'}
    res = requests.post(url, data=json.dumps(payload), cookies=cookies)
    auth= res.json().get("data").get('Auth')
    UserName = res.json().get("data").get('UserName')
    if auth:
        auth_info={'Username':UserName}
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_dept.route('/test',methods =['POST'])
def test():
    if True:
        res = json.dumps({"data":"test","status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
