from models.database import UserDefine, RoleDefine, PermissionDefine, RolePermission, sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
import requests
from datetime import datetime
from modules.common import check_auth

route_role = Blueprint('route_role', __name__)
@route_role.before_request
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
@route_role.route('/getRoleInfobyRoleId',methods =['POST'])
def getRoleInfobyRoleId():
    if True:
        data= json.loads(request.data)
        RoleId = data.get("id")
        
        sql = '''select
                    rd."id",
                    rd."Code" "RoleName",
                    rd."Description",
                    rd."LastUpdateUserName",
                    rd."LastUpdateDateTime"
                from
                    uaa."RoleDefine" rd
                where rd.id = {};'''.format(RoleId)
        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/addRole',methods =['POST'])
def addRole():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        Code = data.get('Code').strip().lower()
        if Code:
            role = RoleDefine.query.filter_by(Code = Code).first()
            if not role:
                payload = {}
                for key, value in data.items():
                    if hasattr(RoleDefine, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower(),'Code':Code})             
                RoleId = RoleDefine(**payload).add()
                role = RoleDefine.query.get(RoleId)
                res = json.dumps({"data": role.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/searchRole',methods =['POST'])
def searchRole():
    if True:
        data= json.loads(request.data)
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        id = data.get("id",0)
        Code = data.get("Code",'')
        Description = data.get("Description",'')
        LastUpdateUserName = data.get("LastUpdateUserName",'')
        LastUpdateDateTime = data.get("LastUpdateDateTime",'')
        if LastUpdateDateTime:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime,'%d/%m/%Y')
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime+' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            LastUpdateDateTime_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            LastUpdateDateTime_T = datetime.now()


        sql = '''select
                    rd."id",
                    rd."Code",
                    rd."Description",
                    rd."LastUpdateUserName",
                    rd."LastUpdateDateTime"
                from
                    uaa."RoleDefine" rd
                where 1=1
                  and (rd.id = {0} or {0} = 0)
                  and (rd."Code" ~ '({1})' or '{1}' = '')
                  and (rd."Description"  ~ '({2})' or '{2}' = '')
                  and (rd."LastUpdateUserName"  ~ '({3})' or '{3}' = '')
                  and (rd."LastUpdateDateTime" >= '{4}' or '{4}' = '')
                  and (rd."LastUpdateDateTime" <= '{5}' or '{5}' = '')
                ORDER BY rd.id
                OFFSET {6} ROWS 
                FETCH FIRST {7} ROW ONLY;'''.format(id,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."RoleDefine" rd
                where 1=1
                  and (rd.id = {0} or {0} = 0)
                  and (rd."Code" ~ '({1})' or '{1}' = '')
                  and (rd."Description"  ~ '({2})' or '{2}' = '')
                  and (rd."LastUpdateUserName"  ~ '({3})' or '{3}' = '')
                  and (rd."LastUpdateDateTime" >= '{4}' or '{4}' = '')
                  and (rd."LastUpdateDateTime" <= '{5}' or '{5}' = '')
                ;'''.format(id,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/updateRolebyRoleId',methods =['POST'])
def updateRolebyRoleId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        RoleId = data.get('id',0)
        role = RoleDefine.query.get(RoleId)
        if role:
            for key, value in data.items():
                    if hasattr(RoleDefine, key):
                        data.update({key:value})
            data.update({'Code':role.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update Code: role.Code để chặn không cho update Code
            role.update(data)
            res = json.dumps({"data":role.json(),"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/changeRolePermissions',methods =['POST'])
def changeRolePermissions():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        RoleId = data.get('RoleId')
        PermissionIds = data.get('PermissionList')
        Description = data.get('Description','')        
        rolepermissions= RolePermission.query.filter_by(RoleId=RoleId).all()
        for rolepermission in rolepermissions:
            rolepermission.remove()
        if PermissionIds:
            for PermissionId in PermissionIds:
                data = {'RoleId':RoleId, 'PermissionId':PermissionId, 'Description':Description}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
                RolePermission(**data).add()
        rolepermissions = []
        for rolepermission in RolePermission.query.filter_by(RoleId=RoleId).all():
            rolepermissions.append(rolepermission.json())
        res = json.dumps({"data":rolepermissions,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/getPermissionsByRoleId',methods =['POST'])
def getPermissionsByRole():
    if True:
        data= json.loads(request.data)
        RoleId = data.get("id")
        sql = '''select
                    rd.id "RoleId",
                    pd.id "PermissionId",
                    pd."Code" "PermissionName"
                from
                    uaa."RoleDefine" rd
                join uaa."RolePermission" rp on
                    rp."RoleId" = rd.id
                join uaa."PermissionDefine" pd on
                    pd.id = rp."PermissionId"
                and pd."PermissionType" = 'ROLE'
                where rd.id = {};'''.format(RoleId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
