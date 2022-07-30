from datetime import datetime, timedelta
from flask import Blueprint, request, session
from config import Config
from werkzeug.wrappers import Response
from bson import json_util
import jwt
import json
from models.database import UserDefine
from modules.common import hashed_password,check_password,getPagesbyUserId,getFunctionbyUserId

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
                    exp=datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS)# truyền vào hàm jwt.encode là gmt, lúc jwt.deceode lại trả ra timezone server(gmt + 7) 
                    UserId = user.id
                    payload.update({'exp': exp,'UserId':UserId})
                    # gen token 4 auth
                    jwt_token = jwt.encode(payload, Config.JWT_SECRET, Config.JWT_ALGORITHM)                    
                    # Response
                    Pages = getPagesbyUserId(user.id)                
                    res = json.dumps({"token": jwt_token.decode('utf-8'),"Pages":Pages,"status":'OK'},default=json_util.default).encode('utf-8')
                    status = 200
                    #init session
                    Functions = getFunctionbyUserId(UserId,'UAA')
                    session["UserId"] = UserId
                    session["UserName"] = UserName
                    session["Pages"] = Pages
                    session["Functions"] = Functions
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
    data = json.loads(request.data)
    UserName = data['UserName'].strip().lower()
    payload = {}
    user = UserDefine.query.filter_by(UserName = UserName).first()
    if not user:
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

@authentication.route('/check_auth_ext',methods =['POST'])
def check_auth_ext():
    if True:
        jwt_token = request.cookies.get('app_token', None)
        auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
        data = json.loads(request.data)
        type = data.get("type")
        UserId =  auth_info.get("UserId")
        Functions = getFunctionbyUserId(UserId,type)
        UserName = auth_info.get('UserName')
        data = {"Functions":Functions,"UserName":UserName}
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)