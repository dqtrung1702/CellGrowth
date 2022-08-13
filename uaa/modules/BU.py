from models.database import UserDefine
from models.database import BU
from models.database import sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
from datetime import datetime
from modules.common import check_auth

route_bu = Blueprint('route_bu', __name__)

@route_bu.before_request
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
@route_bu.route('/getBUInfobyBUId',methods =['POST'])
def getBUInfobyBUId():
    if True:
        data= json.loads(request.data)
        BUId = data.get("id")
        
        sql = '''select
                    bu."id",
                    bu."Code" "BU",
                    bu."Description",
                    bu."LastUpdateUserName",
                    bu."LastUpdateDateTime"
                from
                    uaa."BU" bu
                where bu.id = {};'''.format(BUId)
        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_bu.route('/addBU',methods =['POST'])
def addBU():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        Code = data.get('Code')
        if Code:
            bu = BU.query.filter_by(Code = Code).first()
            if not setrcd:
                payload = {}
                for key, value in data.items():
                    if hasattr(BU, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower(),'Code':Code})                
                SetId = BU(**payload).add()
                setrcd = BU.query.get(SetId)
                res = json.dumps({"data": setrcd.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
        else:
            res = json.dumps({'message': 'Umm...',"status":'FAIL'}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_bu.route('/searchBU',methods =['POST'])
def searchBU():
    if True:
        data= json.loads(request.data)
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        id = data.get("id",0)
        Code = data.get("Code",'')
        Description = data.get("Description",'')
        LastUpdateUserName = data.get("LastUpdateUserName",'')
        LastUpdateDateTime_F = data.get("LastUpdateDateTime_F",'')
        LastUpdateDateTime_T = data.get("LastUpdateDateTime_T",'')
        if LastUpdateDateTime_F:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime_F,'%d/%m/%Y')
        if LastUpdateDateTime_T:
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime_T +' 23:59:59','%d/%m/%Y %H:%M:%S')
        sql = '''select
                    bu."id",
                    bu."Code" "BU",
                    bu."Description",
                    bu."LastUpdateUserName",
                    bu."LastUpdateDateTime"
                from
                    uaa."BU" bu
                where (bu.id = {0} or {0} = 0)
                  and (bu."Code"  ~ '({1})' or '{1}' = '')
                  and (bu."Description"  ~ '({2})' or '{2}' = '')
                  and (bu."LastUpdateUserName"  ~ '({3})' or '{3}' = '')
                  and (bu."LastUpdateDateTime" >= '{4}' or '{4}' = '')
                  and (bu."LastUpdateDateTime" <= '{5}' or '{5}' = '')
                ORDER BY bu.id
                OFFSET {6} ROWS 
                FETCH FIRST {7} ROW ONLY;'''.format(id,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."BU" bu
                where (bu.id = {0} or {0} = 0)
                  and (bu."Code"  ~ '({1})' or '{1}' = '')
                  and (bu."Description"  ~ '({2})' or '{2}' = '')
                  and (bu."LastUpdateUserName"  ~ '({3})' or '{3}' = '')
                  and (bu."LastUpdateDateTime" >= '{4}' or '{4}' = '')
                  and (bu."LastUpdateDateTime" <= '{5}' or '{5}' = '');'''.format(id,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_bu.route('/updateBUbyBUId',methods =['POST'])
def updateBUbyBUId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        BUId = data.get('id',0)
        bu = BU.query.get(BUId)
        if bu:
            itm = {}
            for key, value in data.items():
                    if hasattr(BU, key):
                        itm.update({key:value})
            itm.update({'Code':bu.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update Code: role.Code để chặn không cho update Code
            bu.update(itm)
            data = bu.json()
            res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
