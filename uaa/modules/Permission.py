from models.database import UserDefine
from models.database import RolePermission
from models.database import PermissionDefine
from models.database import RoleDefine
from models.database import URLPermission
from models.database import sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
import requests
from datetime import datetime
from modules.common import check_userurl

route_permission = Blueprint('route_permission', __name__)
@route_permission.before_request
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
@route_permission.route('/getPermissionList',methods =['POST'])
def getPermissionList():
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
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime+' 23:59:59','%d/%m/%Y %H:%M:%S')
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
@route_permission.route('/getPermissionInfo',methods =['POST'])
def getPermissionInfo():
    if True:
        data= json.loads(request.data)
        # PermissionIds = data.getlist("ids")
        PermissionIds = data.get("ids")
        PermissionIds.append('0')
        sql = '''select
                    pd."id",
                    pd."Code" "PermissionName",
                    pd."PermissionType",
                    pd."Description",
                    pd."LastUpdateUserName",
                    pd."LastUpdateDateTime"
                from
                    uaa."PermissionDefine" pd
                where pd."PermissionType" = 'ROLE' 
                  and pd.id in {};'''.format(tuple(PermissionIds))
        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
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
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code']})                
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
@route_permission.route('/getURLbyPermissionList',methods =['POST'])
def getURLbyPermissionList():
    if True:
        data= json.loads(request.data)
        auth_info = request.auth_info
        PermissionList = data.get('PermissionList')
        if PermissionList:
            URLList = []
            for PermissionId in PermissionList:
                for url in URLPermission.query.filter_by(PermissionId= PermissionId).all():
                    URLList.append(url.json())
        res = json.dumps({"data":URLList,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/getURLbyPermission',methods =['POST'])
def getURLbyPermission():
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
@route_permission.route('/getDataPermissionList',methods =['POST'])
def getDataPermissionList():
    if True:
        data= json.loads(request.data)
        Code = data.get("Code","")
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        sql = '''select
                    pd."id",
                    pd."Code"
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and pd."PermissionType" = 'DATA'
                  and pd."Code" ~ '({})'
                ORDER BY pd.id
                OFFSET {} ROWS 
                FETCH FIRST {} ROW ONLY;'''.format(Code,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and pd."PermissionType" = 'DATA'
                  and pd."Code" ~ '({})';
                  '''.format(Code)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/getRolePermissionList',methods =['POST'])
def getRolePermissionList():
    if True:
        data= json.loads(request.data)
        Code = data.get("Code","")
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        sql = '''select
                    pd."id",
                    pd."Code"
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and pd."PermissionType" = 'ROLE'
                  and pd."Code" ~ '({})'
                ORDER BY pd.id
                OFFSET {} ROWS 
                FETCH FIRST {} ROW ONLY;'''.format(Code,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."PermissionDefine" pd
                where 1=1
                  and pd."PermissionType" = 'DATA'
                  and pd."Code" ~ '({})';
                  '''.format(Code)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/updatePermission',methods =['POST'])
def updatePermission():
    if True:
        data = json.loads(request.data)
        PermissionId = data.get('PermissionId')
        Description = data.get('Description','')
        PermissionType = data.get('PermissionType','')
        UrlList = data.get('UrlList','')
        data = {'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()}
        if PermissionId:
            permission = RoleDefine.query.get(PermissionId)
            if permission:
                data.update({'Code':permission.Code,'Description':Description})
                PermissionId=permission.update(data)
        permissionurls= URLPermission.query.filter_by(PermissionId=PermissionId).all()
        for permissionurl in permissionurls:
            permissionurl.remove()
        if UrlList:
            for u in UrlList:
                data = {'RoleId':RoleId, 'PermissionId':PermissionId}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()})
                RolePermission(**data).add()
        res = json.dumps({"data":{'RoleId':RoleId},"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({"message":"Access is denied","status":"FAIL"},default=json_util.default).encode('utf-8')
        status = 403
    return Response(res, mimetype='application/json', status=status)
@route_permission.route('/addPermission',methods =['POST'])
def addPermission():
    if True:
        data = json.loads(request.data)        
        auth_info = request.auth_info
        Code = data.get('Code').strip().lower()
        PermissionType = data.get('PermissionType')
        if Code:
            permission = PermissionDefine.query.filter_by(Code = Code).first()
            if not permission:
                payload = {}
                for key, value in data.items():
                    if hasattr(PermissionDefine, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'],'Code':Code})             
                PermissionId = PermissionDefine(**payload).add()
                
                permission = PermissionDefine.query.get(PermissionId)
                res = json.dumps({"data": permission.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
    return Response(res, mimetype='application/json', status=status)