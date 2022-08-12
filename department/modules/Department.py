from models.database import dept
from flask import Blueprint, request
from bson import json_util
from bson.objectid import ObjectId
import json
from werkzeug.wrappers import Response
from modules.common import check_auth
from datetime import datetime
import pytz

route_dept = Blueprint('route_dept', __name__)

@route_dept.before_request
def before_request_func():
    cookies = request.cookies
    auth,UserName = check_auth(request.url,request.method,cookies)
    if auth:
        auth_info={'UserName':UserName}
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
@route_dept.route('/getDEPTInfobyDEPTId',methods =['POST'])
def getDEPTInfobyDEPTId():
    if True:
        data= json.loads(request.data)
        DEPTId = data.get("id")
        deptinfo = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
        res = json.dumps({"data":deptinfo.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_dept.route('/addDEPT',methods =['POST'])
def addDEPT():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        Code = data.get("Code")
        EFFDT = datetime.strptime(data.get("EFFDT"), "%Y%m%d").astimezone(pytz.utc)#save vào db giờ utc
        Status = data.get("Status")
        ActionCD = data.get("ActionCD")
        Name = data.get("Name")
        ParentId = data.get("ParentId")
        ManagerId = data.get("ManagerId")
        Description = data.get("Description")
        LastUpdateDateTime = datetime.now().astimezone(pytz.utc)
        LastUpdateUserName = auth_info.get('UserName','???').strip().lower()
        dept.db.department.insert_one({
            'Code':Code,
            'EFFDT':EFFDT,
            'Status':Status,
            'ActionCD':ActionCD,
            'Name':Name,
            'ParentId':ParentId,
            'ManagerId': ManagerId,
            'Description':Description,
            'LastUpdateDateTime':LastUpdateDateTime,
            'LastUpdateUserName':LastUpdateUserName
        })
        res = json.dumps({'message':'success'}, default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, status=status)