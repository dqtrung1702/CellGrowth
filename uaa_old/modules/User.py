from requests import session
from models.database import UserDefine
from models.database import UserRole
from models.database import RoleDefine
from models.database import sqlexec
from flask import Blueprint, request,session
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
from datetime import datetime
from modules.common import check_auth,hashed_password

from sqlalchemy.sql import or_

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
        data = UserDefine.query.get(UserId).json()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
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
                user = UserDefine.query.get(UserId).json2(['id', 'UserName', 'NameDisplay', 'UserLocked', 'LastSignOnDateTime', 'LastUpdateUserName', 'LastUpdateDateTime'])
                res = json.dumps({"data": user,"status":'OK'},default=json_util.default).encode('utf-8')
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
        # sql = '''from uaa."UserDefine" ud
        #         where 1=1
        #         '''

        id = data.get("id","")
        # if id:
        #     sql = sql + '''and (ud.id = '{0}')
        #     '''.format(id)

        UserName = data.get("UserName","")
        # if UserName:
        #     sql = sql + '''and (ud."UserName" ~ '{0}')
        #     '''.format(UserName)

        NameDisplay = data.get("NameDisplay","")
        # if NameDisplay:
        #     sql = sql + '''and (ud."NameDisplay" ~ '{0}')
        #     '''.format(NameDisplay)

        UserLocked = data.get("UserLocked","")
        if UserLocked:
            if UserLocked =='Locked':
                UserLocked = True
            else:
                UserLocked = False
            # sql = sql + '''and (ud."UserLocked" = {0})
            # '''.format(NameDisplay)

        LastUpdateUserName = data.get("LastUpdateUserName","")
        # if LastUpdateUserName:
        #     sql = sql + '''and (ud."LastUpdateUserName" ~ '{0}')
        #     '''.format(LastUpdateUserName)

        LastSignOnDateTime_F = data.get("LastSignOnDateTime_F","")
        LastSignOnDateTime_T = data.get("LastSignOnDateTime_T","")

        if LastSignOnDateTime_F:
            LastSignOnDateTime_F = datetime.strptime(LastSignOnDateTime_F,'%d/%m/%Y')
            # sql = sql + '''and (ud."LastSignOnDateTime" >= {0})
            # '''.format(LastSignOnDateTime_F)

        if LastSignOnDateTime_T:
            LastSignOnDateTime_T = datetime.strptime(LastSignOnDateTime_T+' 23:59:59','%d/%m/%Y %H:%M:%S')
            # sql = sql + '''and (ud."LastSignOnDateTime" <= {0})
            # '''.format(LastSignOnDateTime_T)

        LastUpdateDateTime_F = data.get("LastUpdateDateTime_F","")
        LastUpdateDateTime_T = data.get("LastUpdateDateTime_T","")

        if LastUpdateDateTime_F:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime_F,'%d/%m/%Y')
            # sql = sql + '''and (ud."LastUpdateDateTime" >= {0})
            # '''.format(LastUpdateDateTime_F)
        if LastUpdateDateTime_T:
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime_T +' 23:59:59','%d/%m/%Y %H:%M:%S')
            # sql = sql + '''and (ud."LastUpdateDateTime" <= {0})
            # '''.format(LastUpdateDateTime_T)
        page_size = data.get("page_size",10)
        page = data.get("page",1)
        offset = int(page)*int(page_size)-int(page_size) 
        # sql1 = '''
        #         select
        #             ud."id",
        #             ud."UserName",
        #             ud."NameDisplay",
        #             ud."UserLocked",
        #             ud."LastSignOnDateTime",
        #             ud."LastUpdateUserName",
        #             ud."LastUpdateDateTime"
        #         ''' + sql +'''ORDER BY ud.id
        #                OFFSET {0} ROWS 
        #                FETCH FIRST {1} ROW ONLY;'''.format(offset,page_size)
        # sql2 = '''
        #         select
        #             sum(1)
        #         ''' + sql + ''';'''
        query = UserDefine.query.filter(
            or_(UserDefine.id == (id if id else 0), id == ''),
            or_(UserDefine.UserName.like("%"+UserName+"%"), UserName == ''),
            or_(UserDefine.NameDisplay.like("%"+NameDisplay+"%"), NameDisplay == ''),
            (UserDefine.UserLocked == UserLocked if UserLocked != '' else 1 == 1),
            or_(UserDefine.LastUpdateUserName.like("%"+LastUpdateUserName+"%"), LastUpdateUserName == ''),
            or_(UserDefine.LastSignOnDateTime >= LastSignOnDateTime_F, LastSignOnDateTime_F == ''),
            or_(UserDefine.LastSignOnDateTime <= LastSignOnDateTime_T, LastSignOnDateTime_T == ''),
            or_(UserDefine.LastUpdateDateTime >= LastUpdateDateTime_F, LastUpdateDateTime_F == ''),
            or_(UserDefine.LastUpdateDateTime <= LastUpdateDateTime_T, LastUpdateDateTime_T == '')            
            )
        data_raw = query.offset(offset).limit(page_size).all()
        total_row = query.count()
        # data = sqlexec(sql1).json()
        # total_row = sqlexec(sql2).json()
        data = []
        for d in data_raw:
            data.append(d.json2(['id', 'UserName', 'NameDisplay', 'UserLocked', 'LastSignOnDateTime', 'LastUpdateUserName', 'LastUpdateDateTime']))        
        res = json.dumps({"data":data,'total_row':total_row,"status":"OK"},default=json_util.default).encode('utf-8')
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
            data = user.json2(['id', 'UserName', 'NameDisplay', 'UserLocked', 'LastSignOnDateTime', 'LastUpdateUserName', 'LastUpdateDateTime'])
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
        query =  RoleDefine.query.join(UserRole, UserRole.RoleId==RoleDefine.id).filter(UserRole.UserId == UserId)
        data_raw = query.all()
        data = []
        for dr in data_raw:
            d = {"UserId":UserId,"RoleId":dr.id,"Role":dr.Code}
            data.append(d)        
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
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

