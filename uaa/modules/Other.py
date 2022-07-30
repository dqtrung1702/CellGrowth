import models.database
from models.database import UserDefine
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
import requests
from datetime import datetime
from modules.common import check_auth,hashed_password

_other = Blueprint('_other', __name__)
@_other.before_request
def before_request_func():
    # các request tới route_user đều phải qua đây trước
    jwt_token = request.cookies.get('app_token', None)
    auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
    auth,UserName = check_auth(request.url,request.method)
    if auth:
        auth_info.update({'Username':UserName})
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@_other.route('/getTbl',methods =['POST'])
def getTbl():
    if True:
        data = request.form.to_dict(flat=True)
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page_size)*(int(page)-1)
        tbl = data.get("TableName")
        list = eval("models.database.{0}.query.order_by(models.database.{0}.id).limit({1}).offset({2})".format(tbl,page_size,offset))
        records_amount = eval("models.database.{0}.query.count()".format(tbl))
        if list:
            payload = []
            for lst in list:
                l = lst.json()
                payload.append(l)
            res = json.dumps({"data":payload,"records_amount":records_amount,"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":"FAIL"},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@_other.route('/updateTbl',methods =['POST'])
def updateTbl():
    if True:
        data = json.loads(request.data)
        TableName = data.get('TableName')
        TableId = data.get('id',0)
        table = eval('models.database.{}.query.get({})'.format(TableName,TableId))
        if table:
            data.update({'Code':table.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()})
            if TableName == 'UserDefine':
                if data.get('Password'):
                    data.update({'Password':hashed_password(data['Password'])})
                if data.get('UserLocked'):                    
                    data.update({'UserLocked':Config.BOOLEAN.get(data.get('UserLocked'))})
            TableId=table.update(data)
            res = json.dumps({"data":table.json(),"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":"FAIL"},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@_other.route('/addTbl',methods =['POST'])
def addTbl():
    if True:
        data = json.loads(request.data)
        TableName = data['TableName']
        Code = data.get('Code').strip().lower()
        # table = eval('{}.query.filter_by(Code = Code).first()'.format(TableName))
        table = models.database.UserDefine.query.filter_by(Code = Code).first()
        if not table:
            payload = {}
            exec("""for key, value in data.items():\n    if hasattr(models.database."""+TableName+""", key):\n        payload.update({key:value})""")
            payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'],'Code':Code})
            if TableName == 'UserDefine':
                SetId = payload.get('SetId',None)
                DataPermission = payload.get('DataPermission',None)
                Password = hashed_password(payload['Password'])
                UserLocked = payload.get('UserLocked',False)
                payload.update({'LastSignOnDateTime':datetime.now(),'Password':Password,'UserLocked':UserLocked,'SetId':SetId,'DataPermission':DataPermission})
            TableId = eval('models.database.{}(**payload).add()'.format(TableName))
            table = eval('models.database.{}.query.get({})'.format(TableName,TableId))
            res = json.dumps({"data": table.json(),"status":'OK'},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
            status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)

   