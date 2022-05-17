from models.database import UserDefine
from models.database import UserRole
from models.database import RolePermission
from models.database import PermissionDefine
from models.database import SetDefine
from models.database import RoleDefine
from models.database import sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
import requests
from datetime import datetime
from modules.common import check_userurl,hashed_password

route_user = Blueprint('route_user', __name__)

@route_user.before_request
def before_request_func():
    # các request tới route_user đều phải qua đây trước
    jwt_token = request.cookies.get('app_token', None)
    auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
    auth_user = UserDefine.query.filter_by(Code = auth_info['Code']).first()
    if auth_user and check_userurl(auth_info['id'],request.url,'privAPI',request.method):
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_user.route('/addUser',methods =['POST'])
def addUser():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserName = data.get('Code')
        Password = hashed_password(data.get('Password'))
        if UserName and Password:
            user = UserDefine.query.filter_by(Code = UserName).first()
            if not user:
                payload = {}
                for key, value in data.items():
                    if hasattr(UserDefine, key):
                        payload.update({key:value})
                payload.update({'Password':Password, 'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('Code','auto')})                
                
                UserId = UserDefine(**payload).add()
                user = UserDefine.query.get(UserId)
                res = json.dumps({"data": user.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
        else:
            res = json.dumps({'message': 'Umm...',"status":'FAIL'}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/getUserInfo',methods =['POST'])
def getUserInfo():
    if True:
        data= json.loads(request.data)
        UserId = data.get("id")        
        sql = '''select
                    ud."id",
                    ud."Code" "UserName",
                    ud."NameDisplay",
                    ud."UserLocked",
                    ud."LastSignOnDateTime",
                    ud."LastUpdateUserName",
                    ud."LastUpdateDateTime",
                    sd."Code" "SetCode",
                    ud."DataPermission" "DataPermissionId",
                    pd."Code" "DataPermission"
                from
                    uaa."UserDefine" ud
                left join uaa."SetDefine" sd on
                    sd."id" = ud."SetId"
                left join uaa."PermissionDefine" pd on
                    pd."id" = ud."DataPermission"
                and pd."PermissionType" = 'DATA'
                where ud.id = {};'''.format(UserId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/getUserList',methods =['POST'])
def getUserList():
    if True:
        data= json.loads(request.data)
        auth_info = request.auth_info
        id = data.get("id",0)
        Code = data.get("Code",'')
        NameDisplay = data.get("NameDisplay",'')

        if data.get("UserLocked") =='Locked':
            UserLocked = True
        elif data.get("UserLocked") =='UnLocked':
            UserLocked = False
        else:
            UserLocked = 'ud."UserLocked"'
        LastUpdateUserName = data.get("LastUpdateUserName",'')

        LastSignOnDateTime = data.get("LastSignOnDateTime",'')
        if LastSignOnDateTime:
            LastSignOnDateTime_F = datetime.strptime(LastSignOnDateTime,'%d/%m/%Y')
            LastSignOnDateTime_T = datetime.strptime(LastSignOnDateTime+' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            LastSignOnDateTime_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            LastSignOnDateTime_T = datetime.now()
        LastUpdateDateTime = data.get("LastUpdateDateTime",'')
        if LastUpdateDateTime:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime,'%d/%m/%Y')
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime+' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            LastUpdateDateTime_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            LastUpdateDateTime_T = datetime.now()

        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        sql = '''select
                    ud."id",
                    ud."Code",
                    ud."NameDisplay",
                    ud."UserLocked",
                    ud."LastSignOnDateTime",
                    ud."LastUpdateUserName",
                    ud."LastUpdateDateTime"
                from
                    uaa."UserDefine" ud
                where 1=1
                and (ud.id = {0} or {0} = 0)
                and (ud."Code"  ~ '({1})' or '{1}' = '')
                and (ud."NameDisplay"  ~ '({2})' or '{2}' = '')
                and (ud."UserLocked" = {3})
                and (ud."LastUpdateUserName"  ~ '({4})' or '{4}' = '')
                and (ud."LastSignOnDateTime" >= '{5}' or '{5}' = '')
                and (ud."LastSignOnDateTime" <= '{6}' or '{6}' = '')
                and (ud."LastUpdateDateTime" >= '{7}' or '{7}' = '')
                and (ud."LastUpdateDateTime" <= '{8}' or '{8}' = '')
                ORDER BY ud.id
                OFFSET {9} ROWS 
                FETCH FIRST {10} ROW ONLY;'''.format(id,Code,NameDisplay,UserLocked,LastUpdateUserName,LastSignOnDateTime_F,LastSignOnDateTime_T,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select
                    sum(1)
                from
                    uaa."UserDefine" ud
                where 1=1
                and (ud.id = {0} or {0} = 0)
                and (ud."Code"  ~ '({1})' or '{1}' = '')
                and (ud."NameDisplay"  ~ '({2})' or '{2}' = '')
                and (ud."UserLocked" = {3})
                and (ud."LastUpdateUserName"  ~ '({4})' or '{4}' = '')
                and (ud."LastSignOnDateTime" >= '{5}' or '{5}' = '')
                and (ud."LastSignOnDateTime" <= '{6}' or '{6}' = '')
                and (ud."LastUpdateDateTime" >= '{7}' or '{7}' = '')
                and (ud."LastUpdateDateTime" <= '{8}' or '{8}' = '')
                ;'''.format(id,Code,NameDisplay,UserLocked,LastUpdateUserName,LastSignOnDateTime_F,LastSignOnDateTime_T,LastUpdateDateTime_F,LastUpdateDateTime_T)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),'total_row':total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/updateUser',methods =['POST'])
def updateUser():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserId = data.get('id',0)
        user = UserDefine.query.get(UserId)
        if user:
            for key, value in data.items():
                    if hasattr(UserDefine, key):
                        data.update({key:value})
            data.update({'Code':user.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()})
            if data.get('Password'):
                data.update({'Password':hashed_password(data['Password'])})
            if data.get('UserLocked'):
                data.update({'UserLocked':Config.BOOLEAN.get(data.get('UserLocked'))})
            user.update(data)
            res = json.dumps({"data":user.json(),"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/getRoleByUser',methods =['POST'])
def getRoleByUser():
    if True:
        data = json.loads(request.data)
        UserId = data.get("id")
        sql = '''select
                    ur."UserId",
                    ur."RoleId",
                    ur.id "UserRoleId",
                    rd."Code" "Role"
                from
                    uaa."UserDefine" ud
                join uaa."UserRole" ur on
                    ur."UserId" = ud.id
                join uaa."RoleDefine" rd on
                    rd.id = ur."RoleId"
                where ud.id = {};'''.format(UserId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/getUserByRole',methods =['POST'])
def getUserByRole():
    if True:
        data = json.loads(request.data)
        RoleId = data.get("id")
        sql = '''select
                    ur."UserId",
                    ur."RoleId",
                    ud."Code" "UserName"
                from
                    uaa."UserDefine" ud
                join uaa."UserRole" ur on
                    ur."UserId" = ud.id
                where ur."RoleId" = {};'''.format(RoleId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/addUserRole',methods =['POST'])
def addUserRole():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserId = data.get('UserId')
        RoleId = data.get('RoleId')
        if UserId and RoleId:
            userrole = UserRole.query.filter_by(UserId = UserId,RoleId = RoleId).first()
            if not userrole:
                payload = {}
                for key, value in data.items():
                    if hasattr(UserRole, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code']})                
                UserRoleId = UserRole(**payload).add()
                userrole = UserRole.query.get(UserRoleId)
                res = json.dumps({"data": userrole.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/updateUserRole',methods =['POST'])
def updateUserRole():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserId = data.get('UserId')
        RoleList = data.get('RoleList')
        userroles= UserRole.query.filter_by(UserId=UserId).all()
        for userrole in userroles:
            userrole.remove()        
        if RoleList:
            for role in RoleList:
                data = {'UserId':UserId, 'RoleId':role}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info['Code'].strip().lower()})
                UserRole(**data).add()
        userroles = []
        for userrole in UserRole.query.filter_by(UserId=UserId).all():
            userroles.append(userrole.json())
        res = json.dumps({"data":userroles,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)