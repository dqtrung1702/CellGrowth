from models.database import UserDefine
from models.database import PermissionDefine
from models.database import URLPermission
from models.database import DataPermission
from models.database import sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
from datetime import datetime
from modules.common import check_auth

route_permission = Blueprint('route_permission', __name__)
@route_permission.before_request
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
@route_permission.route('/searchPermission',methods =['POST'])
def searchPermission():
    if True:        
        data= json.loads(request.data)
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        id = data.get("id",0)
        Code = data.get("Code",'')
        PermissionType = data.get("PermissionType","")
        Description = data.get("Description",'')
        LastUpdateUserName = data.get("LastUpdateUserName",'')
        LastUpdateDateTime = data.get("LastUpdateDateTime",'')
        if LastUpdateDateTime:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime,'%d/%m/%Y')
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime +' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            LastUpdateDateTime_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            LastUpdateDateTime_T = datetime.now()

        sql = '''select
                    pd."id",
                    pd."Code",
                    pd."PermissionType",
                    pd."Description",
                    pd."LastUpdateUserName",
                    pd."LastUpdateDateTime"
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and (pd.id = {0} or {0} = 0)
                  and (pd."Code" ~ '({1})' or '{1}' = '')
                  and (pd."PermissionType"  ~ '({2})' or '{2}' = '')
                  and (pd."Description"  ~ '({3})' or '{3}' = '')
                  and (pd."LastUpdateUserName"  ~ '({4})' or '{5}' = '')
                  and (pd."LastUpdateDateTime" >= '{5}' or '{5}' = '')
                  and (pd."LastUpdateDateTime" <= '{6}' or '{6}' = '')
                ORDER BY pd.id
                OFFSET {7} ROWS 
                FETCH FIRST {8} ROW ONLY;'''.format(id,Code,PermissionType,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and (pd.id = {0} or {0} = 0)
                  and (pd."Code" ~ '({1})' or '{1}' = '')
                  and (pd."PermissionType"  ~ '({2})' or '{2}' = '')
                  and (pd."Description"  ~ '({3})' or '{3}' = '')
                  and (pd."LastUpdateUserName"  ~ '({4})' or '{5}' = '')
                  and (pd."LastUpdateDateTime" >= '{5}' or '{5}' = '')
                  and (pd."LastUpdateDateTime" <= '{6}' or '{6}' = '')
                  '''.format(id,Code,PermissionType,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/addPermission',methods =['POST'])
def addPermission():
    if True:
        data = json.loads(request.data)        
        auth_info = request.auth_info
        Code = data.get('Code').strip().lower()
        if Code:
            permission = PermissionDefine.query.filter_by(Code = Code).first()
            if not permission:
                payload = {}
                for key, value in data.items():
                    if hasattr(PermissionDefine, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower(),'Code':Code})             
                PermissionId = PermissionDefine(**payload).add()
                
                permission = PermissionDefine.query.get(PermissionId)
                res = json.dumps({"data": permission.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/updatePermissionbyPermissionId',methods =['POST'])
def updatePermissionbyPermissionId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        PermissionId = data.get('id',0)
        permission = PermissionDefine.query.get(PermissionId)
        if permission:
            for key, value in data.items():
                    if hasattr(PermissionDefine, key):
                        data.update({key:value})
            data.update({'Code':permission.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update Code: role.Code để chặn không cho update Code
            permission.update(data)
            res = json.dumps({"data":role.json(),"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/searchURLPermission',methods =['POST'])
def searchURLPermission():
    if True:        
        data= json.loads(request.data)
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        id = data.get("id",0)
        EFFFDate = data.get("EFFFDate",'')
        EFFTDate = data.get("EFFTDate",'')
        PermissionId = data.get("PermissionId",0)
        url = data.get("url",'')
        Method = data.get("Method","")
        Type = data.get("Type","")
        Description = data.get("Description",'')
        LastUpdateUserName = data.get("LastUpdateUserName",'')
        LastUpdateDateTime = data.get("LastUpdateDateTime",'')
        if LastUpdateDateTime:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime,'%d/%m/%Y')
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime +' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            LastUpdateDateTime_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            LastUpdateDateTime_T = datetime.now()
        if EFFFDate:
            EFFFDate_F = datetime.strptime(EFFFDate,'%d/%m/%Y')
            EFFFDate_T = datetime.strptime(EFFFDate +' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            EFFFDate_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            EFFFDate_T = datetime.now()
        if EFFTDate:
            EFFTDate_F = datetime.strptime(EFFTDate,'%d/%m/%Y')
            EFFTDate_T = datetime.strptime(EFFTDate +' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            EFFTDate_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            EFFTDate_T = datetime.now()
        PermissionId = data.get("PermissionId",0)
        sql = '''select
                    up."id",
                    up."EFFFDate",
                    up."EFFTDate",
                    up."PermissionId",
                    up."url",
                    up."Method",
                    up."Type",
                    up."Description",
                    up."LastUpdateUserName",
                    up."LastUpdateDateTime"
                from
                    uaa."UrlPermission" up
                where 1=1
                  and (up.id = {0} or {0} = 0)
                  and (up."EFFFDate" >= '{1}' or '{1}' = '')
                  and (up."EFFFDate" <= '{2}' or '{2}' = '')
                  and (up."EFFTDate" >= '{3}' or '{3}' = '')
                  and (up."EFFTDate" <= '{4}' or '{4}' = '')
                  and (up.PermissionId = {5} or {5} = 0)
                  and (up."url" ~ '({6})' or '{6}' = '')
                  and (up."Method" ~ '({7})' or '{7}' = '')
                  and (up."Type"  ~ '({8})' or '{8}' = '')
                  and (up."Description"  ~ '({9})' or '{9}' = '')
                  and (up."LastUpdateUserName"  ~ '({10})' or '{10}' = '')
                  and (up."LastUpdateDateTime" >= '{11}' or '{11}' = '')
                  and (up."LastUpdateDateTime" <= '{12}' or '{12}' = '')
                ORDER BY up.id
                OFFSET {13} ROWS 
                FETCH FIRST {14} ROW ONLY;'''.format(id,EFFFDate_F,EFFFDate_T,EFFTDate_F,EFFTDate_T,PermissionId,url,Method,Type,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and (up.id = {0} or {0} = 0)
                  and (up."EFFFDate" >= '{1}' or '{1}' = '')
                  and (up."EFFFDate" <= '{2}' or '{2}' = '')
                  and (up."EFFTDate" >= '{3}' or '{3}' = '')
                  and (up."EFFTDate" <= '{4}' or '{4}' = '')
                  and (up.PermissionId = {5} or {5} = 0)
                  and (up."url" ~ '({6})' or '{6}' = '')
                  and (up."Method" ~ '({7})' or '{7}' = '')
                  and (up."Type"  ~ '({8})' or '{8}' = '')
                  and (up."Description"  ~ '({9})' or '{9}' = '')
                  and (up."LastUpdateUserName"  ~ '({10})' or '{10}' = '')
                  and (up."LastUpdateDateTime" >= '{11}' or '{11}' = '')
                  and (up."LastUpdateDateTime" <= '{12}' or '{12}' = '')
                  '''.format(id,EFFFDate_F,EFFFDate_T,EFFTDate_F,EFFTDate_T,PermissionId,url,Method,Type,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/addURLPermission',methods =['POST'])
def addURLPermission():
    if True:
        data= json.loads(request.data)
        auth_info = request.auth_info
        url = data.get('url').strip().lower()
        data.update({"url":url})
        PermissionId = data.get('PermissionId')
        if url and PermissionId:
            urlpermission = URLPermission.query.filter_by(url = url,PermissionId = PermissionId).first()
            if not urlpermission:
                payload = {}
                for key, value in data.items():
                    if hasattr(URLPermission, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})                
                URLPermissionId = URLPermission(**payload).add()
                urlpermission = URLPermission.query.get(URLPermissionId)
                res = json.dumps({"data": urlpermission.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
        else:
            res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
            status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/getURLbyPermissionId',methods =['POST'])
def getURLbyPermissionId():
    if True:
        data= json.loads(request.data)
        PermissionId = data.get("PermissionId")
        sql = '''select
                    up."id",
                    up."PermissionId",
                    pd."Code" "PermissionRole",
                    up."url",
                    up."Method",
                    up."Type",
                    up."Description",
                    up."LastUpdateUserName",
                    up."LastUpdateDateTime"
                from uaa."PermissionDefine" pd
                join uaa."URLPermission" up on
                    pd.id = up."PermissionId" 
                and pd."PermissionType" = 'ROLE'
                where pd.id = {};'''.format(PermissionId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/updateURLbyURLId',methods =['POST'])
def updateURLbyURLId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UrlPermissionId = data.get('id',0)
        urlpermission = URLPermission.query.get(UrlPermissionId)
        if role:
            for key, value in data.items():
                    if hasattr(URLPermission, key):
                        data.update({key:value})
            data.update({'PermissionId':URLPermission.PermissionId,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update PermissionId: URLPermission.PermissionId để chặn không cho update PermissionId
            urlpermission.update(data)
            res = json.dumps({"data":urlpermission.json(),"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/changeUserDataPermissions',methods =['POST'])
def changeUserDataPermissions():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserId = data.get('UserId')
        PermissionIds = data.get('PermissionList')
        Description = data.get('Description','')        
        datapermissions= DataPermission.query.filter_by(UserId=UserId).all()
        for datapermission in datapermissions:
            datapermission.remove()
        if PermissionIds:
            for PermissionId in PermissionIds:
                data = {'UserId':UserId, 'PermissionId':PermissionId, 'Description':Description}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
                DataPermission(**data).add()
        datapermissions = []
        for datapermission in DataPermission.query.filter_by(UserId=UserId).all():
            datapermissions.append(datapermission.json())
        res = json.dumps({"data":datapermissions,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)