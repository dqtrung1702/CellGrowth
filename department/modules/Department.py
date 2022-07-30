from models.database import db
from flask import Blueprint, request
from bson import json_util
import json
from werkzeug.wrappers import Response
from modules.common import check_auth

route_dept = Blueprint('route_dept', __name__)

@route_dept.before_request
def before_request_func():
    cookies = request.cookies
    auth,UserName = check_auth(request.url,request.method,cookies)
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
