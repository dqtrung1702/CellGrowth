from requests import session
from models.database import UserDefine
from models.database import UserRole
from models.database import sqlexec
from flask import Blueprint, request,session
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
from datetime import datetime
from modules.common import check_auth,hashed_password

route_user = Blueprint('route_user', __name__)

@route_user.before_request
def before_request_func():
    # các request tới route_user đều phải qua đây trước
    jwt_token = request.cookies.get('app_token', None)
    auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
    auth,UserName = check_auth(request.url,request.method)
    if auth:
        auth_info.update({'UserName':UserName})
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_user.route('/getUserInfobyUserId',methods =['POST'])
def getUserInfobyUserId():
    if True:
        data= json.loads(request.data)
        UserId = data.get("UserId")        
        sql = '''select
                    ud."id",
                    ud."UserName",
                    ud."NameDisplay",
                    ud."PersonId",
                    ud."UserLocked",
                    ud."LastSignOnDateTime",
                    ud."LastUpdateUserName",
                    ud."LastUpdateDateTime"
                from
                    uaa."UserDefine" ud
                where ud.id = {} ;'''.format(UserId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/addUser',methods =['POST'])
def addUser():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserName = data.get('UserName')
        Password = hashed_password(data.get('Password'))
        if UserName and Password:
            user = UserDefine.query.filter_by(UserName = UserName).first()
            if not user:
                payload = {}
                for key, value in data.items():
                    if hasattr(UserDefine, key):
                        payload.update({key:value})
                payload.update({'Password':Password, 'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???')})                
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
@route_user.route('/searchUser',methods =['POST'])
def searchUser():
    if True:
        data= json.loads(request.data)
        auth_info = request.auth_info
        id = data.get("id",0)
        UserName = data.get("UserName",'')
        NameDisplay = data.get("NameDisplay",'')

        if data.get("UserLocked") =='Locked':
            UserLocked = True
        elif data.get("UserLocked") =='UnLocked':
            UserLocked = False
        else:
            UserLocked = 'ud."UserLocked"'
        LastUpdateUserName = data.get("LastUpdateUserName",'')

        LastSignOnDateTime_F = data.get("LastSignOnDateTime_F",'')
        LastSignOnDateTime_T = data.get("LastSignOnDateTime_T",'')
        if LastSignOnDateTime_F:
            LastSignOnDateTime_F = datetime.strptime(LastSignOnDateTime_F,'%d/%m/%Y')
        if LastSignOnDateTime_T:            
            LastSignOnDateTime_T = datetime.strptime(LastSignOnDateTime_T+' 23:59:59','%d/%m/%Y %H:%M:%S')
        LastUpdateDateTime_F = data.get("LastUpdateDateTime_F",'')
        LastUpdateDateTime_T = data.get("LastUpdateDateTime_T",'')
        if LastUpdateDateTime_F:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime_F,'%d/%m/%Y')
        if LastUpdateDateTime_T:
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime_T +' 23:59:59','%d/%m/%Y %H:%M:%S')
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        sql = '''select
                    ud."id",
                    ud."UserName",
                    ud."NameDisplay",
                    ud."UserLocked",
                    ud."LastSignOnDateTime",
                    ud."LastUpdateUserName",
                    ud."LastUpdateDateTime"
                from
                    uaa."UserDefine" ud
                where 1=1
                and (ud.id = {0} or {0} = 0)
                and (ud."UserName"  ~ '({1})' or '{1}' = '')
                and (ud."NameDisplay"  ~ '({2})' or '{2}' = '')
                and (ud."UserLocked" = {3})
                and (ud."LastUpdateUserName"  ~ '({4})' or '{4}' = '')
                and (ud."LastSignOnDateTime" >= '{5}' or '{5}' = '')
                and (ud."LastSignOnDateTime" <= '{6}' or '{6}' = '')
                and (ud."LastUpdateDateTime" >= '{7}' or '{7}' = '')
                and (ud."LastUpdateDateTime" <= '{8}' or '{8}' = '')
                ORDER BY ud.id
                OFFSET {9} ROWS 
                FETCH FIRST {10} ROW ONLY;'''.format(id,UserName,NameDisplay,UserLocked,LastUpdateUserName,LastSignOnDateTime_F,LastSignOnDateTime_T,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select
                    sum(1)
                from
                    uaa."UserDefine" ud
                where 1=1
                and (ud.id = {0} or {0} = 0)
                and (ud."UserName"  ~ '({1})' or '{1}' = '')
                and (ud."NameDisplay"  ~ '({2})' or '{2}' = '')
                and (ud."UserLocked" = {3})
                and (ud."LastUpdateUserName"  ~ '({4})' or '{4}' = '')
                and (ud."LastSignOnDateTime" >= '{5}' or '{5}' = '')
                and (ud."LastSignOnDateTime" <= '{6}' or '{6}' = '')
                and (ud."LastUpdateDateTime" >= '{7}' or '{7}' = '')
                and (ud."LastUpdateDateTime" <= '{8}' or '{8}' = '')
                ;'''.format(id,UserName,NameDisplay,UserLocked,LastUpdateUserName,LastSignOnDateTime_F,LastSignOnDateTime_T,LastUpdateDateTime_F,LastUpdateDateTime_T)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),'total_row':total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/updateUserbyUserId',methods =['POST'])
def updateUserbyUserId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserId = data.get('UserId',0)
        user = UserDefine.query.get(UserId)
        if user:
            itm = {}
            for key, value in data.items():
                    if hasattr(UserDefine, key):
                        itm.update({key:value})
            itm.update({'UserName':user.UserName,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update UserName: user.UserName để chặn không cho update UserName
            if data.get('Password'):
                itm.update({'Password':hashed_password(data['Password'])})
            if data.get('UserLocked'):
                itm.update({'UserLocked':Config.BOOLEAN.get(data.get('UserLocked'))})
            user.update(itm)
            data = user.json()
            res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/getRolesByUserId',methods =['POST'])
def getRolesByUserId():
    if True:
        data = json.loads(request.data)
        UserId = data.get("UserId")
        sql = '''select
                    ur."UserId",
                    ur."RoleId",
                    rd."Code" "Role"
                from
                    uaa."UserRole" ur
                join uaa."RoleDefine" rd on
                    rd.id = ur."RoleId"
                where ur.UserId = {};'''.format(UserId)        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_user.route('/changeUserRoles',methods =['POST'])
def changeUserRoles():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        UserId = data.get('UserId')
        RoleList = data.get('RoleList')
        Description = data.get('Description','')
        userroles= UserRole.query.filter_by(UserId=UserId).all()
        for userrole in userroles:
            userrole.remove()        
        if RoleList:
            for role in RoleList:
                data = {'UserId':UserId, 'RoleId':role, 'Description':Description}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
                UserRole(**data).add()
        userroles = []
        for userrole in UserRole.query.filter_by(UserId=UserId).all():
            userroles.append(userrole.json())
        res = json.dumps({"data":userroles,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)

