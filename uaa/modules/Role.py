from models.database import UserDefine, RoleDefine, PermissionDefine, UserRole, RolePermission, URLPermission, sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
import requests
from datetime import datetime
from modules.common import check_userurl

route_role = Blueprint('route_role', __name__)
@route_role.before_request
def before_request_func():
    jwt_token = request.cookies.get('app_token', None)
    auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
    auth_user = UserDefine.query.filter_by(Code = auth_info['Code']).first()
    if auth_user and check_userurl(auth_info['id'],request.url,'privAPI',request.method):
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_role.route('/getRoleList',methods =['POST'])
def getRoleList():
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
@route_role.route('/deleteRoleById',methods =['POST'])
def deleteRoleById():
    if True:
        data= json.loads(request.data)
        RoleId = data.get("id")
        role =  RoleDefine.query.get(RoleId)
        rolepermissions= RolePermission.query.filter_by(RoleId=RoleId).all()
        userroles = UserRole.query.filter_by(RoleId=RoleId).all()
        RoleId = role.remove()
        RolePermissionIds = []
        for rolepermission in rolepermissions:
            RolePermissionId = rolepermission.remove()
            RolePermissionIds.append(RolePermissionId)
        UserRoleIds = []
        for userrole in userroles:
            UserRoleId = userrole.remove()
            UserRoleIds.append(UserRoleId)
        res = json.dumps({"data":{'RoleId':RoleId,'RolePermissionIds':RolePermissionIds,'UserRoleIds':UserRoleIds},"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/getRoleInfo',methods =['POST'])
def getRoleInfo():
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
@route_role.route('/updateRole',methods =['POST'])
def updateRole():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        RoleId = data.get('RoleId')
        PermissionIds = data.get('Permission')
        Description = data.get('Description','')
        data = {'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()}
        if RoleId:
            role = RoleDefine.query.get(RoleId)
            if role:
                data.update({'Code':role.Code,'Description':Description})
                RoleId=role.update(data)
        rolepermissions= RolePermission.query.filter_by(RoleId=RoleId).all()
        for rolepermission in rolepermissions:
            rolepermission.remove()
        if PermissionIds:
            for PermissionId in PermissionIds:
                data = {'RoleId':RoleId, 'PermissionId':PermissionId}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()})
                RolePermission(**data).add()
        res = json.dumps({"data":{'RoleId':RoleId},"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/addRole',methods =['POST'])
def addRole():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        Code = data.get('Code').strip().lower()
        Permission = data.get('Permission')
        if Code:
            role = RoleDefine.query.filter_by(Code = Code).first()
            if not role:
                payload = {}
                for key, value in data.items():
                    if hasattr(RoleDefine, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'],'Code':Code})             
                RoleId = RoleDefine(**payload).add()
                role = RoleDefine.query.get(RoleId)
                res = json.dumps({"data": role.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/addRolePermission',methods =['POST'])
def addRolePermission():
    if True:
        data= json.loads(request.data)
        auth_info = request.auth_info
        PermissionId = data.get('PermissionId')
        RoleId = data.get('RoleId')
        if PermissionId and RoleId:
            rolepermission = RolePermission.query.filter_by(PermissionId = PermissionId,RoleId = RoleId).first()
            if not rolepermission:
                payload = {}
                for key, value in data.items():
                    if hasattr(RolePermission, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code']})                
                RolePermissionId = RolePermission(**payload).add()
                rolepermission = RolePermission.query.get(RolePermissionId)
                res = json.dumps({"data": rolepermission.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
    return Response(res, mimetype='application/json', status=status)
@route_role.route('/getPermissionByRole',methods =['POST'])
def getPermissionByRole():
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
@route_role.route('/getRoleByPermission',methods =['POST'])
def getRoleByPermission():
    if True:
        data= json.loads(request.data)
        PermissionId = data.get("id")
        sql = '''select
                    rp."UserId",
                    rp."RoleId",
                    rd."Code" "RoleName"
                from
                    uaa."RoleDefine" rd
                join uaa."RolePermission" rp on
                    rp."UserId" = rd.id
                where rp."PermissionId" = {};'''.format(PermissionId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
