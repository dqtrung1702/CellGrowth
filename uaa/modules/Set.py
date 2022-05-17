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

route_set = Blueprint('route_set', __name__)

@route_set.before_request
def before_request_func():
    # các request tới route_set đều phải qua đây trước
    jwt_token = request.cookies.get('app_token', None)
    auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
    auth_user = UserDefine.query.filter_by(Code = auth_info['Code']).first()
    if auth_user and check_userurl(auth_info['id'],request.url,'privAPI',request.method):
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_set.route('/addSet',methods =['POST'])
def addSet():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        SetName = data.get('Code')
        if SetName:
            setrcd = SetDefine.query.filter_by(Code = SetName).first()
            if not setrcd:
                payload = {}
                for key, value in data.items():
                    if hasattr(SetDefine, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('Code','import')})                
                SetId = SetDefine(**payload).add()
                setrcd = SetDefine.query.get(SetId)
                res = json.dumps({"data": setrcd.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
        else:
            res = json.dumps({'message': 'Umm...',"status":'FAIL'}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
