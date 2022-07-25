from datetime import datetime, timedelta
from flask import Blueprint, request
from config import Config
from werkzeug.wrappers import Response
from bson import json_util
import jwt
import json
from models.database import sqlexec
from models.database import UserDefine
from models.database import UserRole
from models.database import RolePermission
from modules.common import hashed_password,check_password

authentication = Blueprint('authentication', __name__)


#Login
@authentication.route('/login', methods = ['POST'])
def login():
    data = json.loads(request.data)
    if data:
        UserName = data['UserName'].strip().lower()
        user = UserDefine.query.filter_by(UserName = UserName).first()
        if user:
            if not user.UserLocked:
                if check_password(user.Password,data['Password']):
                    # last signon time
                    user.update({"LastSignOnDateTime":datetime.now()})
                    payload = {}
                    # basic info
                    payload.update({'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS)})# truyền vào hàm jwt.encode là gmt, lúc jwt.deceode lại trả ra timezone server(gmt + 7) 
                    
                    payload.update({'UserId':user.id,'DataPermission':user.DataPermission})
                    # gen token 4 auth
                    jwt_token = jwt.encode(payload, Config.JWT_SECRET, Config.JWT_ALGORITHM)
                    # Response
                    res = json.dumps({"token": jwt_token.decode('utf-8'),"Pages":getPagesbyUserId(user.id),"status":'OK'},default=json_util.default).encode('utf-8')
                    status = 200
                else:
                    res = json.dumps({"message":"Password is incorrect","status":"FAIL"},default=json_util.default).encode('utf-8')
                    status = 200
            else:
                res = json.dumps({"message":"User is locked","status":"FAIL"},default=json_util.default).encode('utf-8')
                status = 200
        else:
            res = json.dumps({"message":"User is incorrect","status":"FAIL"},default=json_util.default).encode('utf-8')
            status = 200
    else:
        res = json.dumps({"message":"Request no Content","status":"FAIL"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)

#Register
@authentication.route('/register',methods =['POST'])
def register():
    print(request.data)
    data = json.loads(request.data)
    UserName = data['UserName'].strip().lower()
    print(UserName)
    payload = {}
    user = UserDefine.query.filter_by(UserName = UserName).first()
    if not user:
        print(UserName)
        UserId = UserDefine(
            UserName = UserName,
            DataPermission = None,
            Password = hashed_password(data['Password']),
            UserLocked = False,
            NameDisplay = data.get('NameDisplay',''),
            LastSignOnDateTime = datetime.now(),
            LastUpdateUserName = UserName,
            LastUpdateDateTime = datetime.now()
        ).add()
        user = UserDefine.query.get(UserId)
        payload = {}
        payload.update(user.json())
        payload.update({'exp': datetime.now() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS)})
        jwt_token = jwt.encode(payload, Config.JWT_SECRET, Config.JWT_ALGORITHM)
        res = json.dumps({"token": jwt_token.decode('utf-8'),"status":'OK'},default=json_util.default).encode('utf-8')
        status = 200
    else:
        res = json.dumps({'message': 'UserName is existed',"status":'FAIL'}, default=json_util.default)
        status = 200
    return Response(res, mimetype='application/json', status=status)

def getPagesbyUserId(UserId):
    if True:
        sql = '''select
                    url
                from
                    uaa."UserRole" ur
                join uaa."RolePermission" rp on
                    rp."RoleId" = ur."RoleId"
                join uaa."URLPermission" up on
                    up."PermissionId" = rp."PermissionId"
                    and up."Type" = 'Page'
                where ur."UserId" = {};'''.format(UserId)
        Pages = list(set([page.get('url') for page in sqlexec(sql).json()]))
    return Pages