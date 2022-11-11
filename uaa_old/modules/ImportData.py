from models.database import UserDefine
from models.database import UserRole
from models.database import RolePermission
from models.database import PermissionDefine
from models.database import URLPermission
from models.database import SetTbl
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
from modules.common import check_auth,hashed_password

route_import = Blueprint('route_import', __name__)

@route_import.before_request
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
@route_import.route('/importUser',methods =['POST'])
def importUser():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        url = Config.UAA_URL
        info=[]
        if data:
            for user in data:
                userinfo = {}
                UserName = user.get("Code").strip().lower()
                usr = UserDefine.query.filter_by(Code = UserName).first()
                
                if not usr:
                    Password = user.get("Password")
                    NameDisplay = user.get("NameDisplay")
                    DataPermission = user.get("DataPermission")
                    user_pay_load = {"Code": UserName,"Password": Password,"NameDisplay": NameDisplay}
                    user_res = requests.post(url+'addUser', data=json.dumps(user_pay_load), cookies = request.cookies)
                    if user_res.status_code == 200 and user_res.json().get('status','') == 'OK':
                        usr = UserDefine.query.filter_by(Code = UserName).first()
                        
                UserId = usr.id                
                rolesinfo = []
                roles = user.get('RolePermission')
                if roles:
                    for role in roles:
                        roleinfo = {}
                        RoleCode = role.get('Code').strip().lower()
                        rol = RoleDefine.query.filter_by(Code = RoleCode).first()
                        
                        if not rol:
                            Description = role.get('Description')
                            role_pay_load = {"Code":RoleCode,"Description":Description}
                            role_res = requests.post(url+'addRole', data=json.dumps(role_pay_load), cookies = request.cookies)
                            if role_res.status_code == 200 and role_res.json().get('status','') == 'OK':
                                rol = RoleDefine.query.filter_by(Code = RoleCode).first()
                        RoleId = rol.id
                        roleinfo.update(rol.json())
                        permissionsinfo = []
                        permissions = role.get('Permission')
                        if permissions:
                            for permission in permissions:
                                permissioninfo = {}
                                PermissionCode = permission.get('Code').strip().lower()
                                prmsn = PermissionDefine.query.filter_by(Code = PermissionCode).first()
                                if not prmsn:
                                    PermissionType = 'ROLE'
                                    Description = permission.get('Description')
                                    prmsn_pay_load = {"Code":PermissionCode,"PermissionType":PermissionType,"Description":Description}
                                    prmsn_res = requests.post(url+'addPermission', data=json.dumps(prmsn_pay_load), cookies = request.cookies)
                                    if prmsn_res.status_code == 200 and prmsn_res.json().get('status','') == 'OK':
                                        prmsn = PermissionDefine.query.filter_by(Code = PermissionCode).first()                                
                                PermissionId = prmsn.id
                                permissioninfo.update(prmsn.json())
                                permissionsinfo.append(permissioninfo)                        
                                rolprmsn = RolePermission.query.filter_by(RoleId = RoleId, PermissionId = PermissionId).first()
                                if not rolprmsn:
                                    rolprmsn_pay_load = {
                                        "PermissionId":PermissionId,
                                        "RoleId":RoleId,
                                        'LastUpdateDateTime':datetime.now(),
                                        'LastUpdateUserName':auth_info['Code']
                                    }                                    
                                    RolePermission(**rolprmsn_pay_load).add()
                                    rolprmsn = RolePermission.query.filter_by(RoleId = RoleId, PermissionId = PermissionId).first()
                                urlpermissions = permission.get('UrlPermission',[])
                                if urlpermissions:
                                    for urlpermission in urlpermissions:
                                        urlpermission.update({"PermissionId":PermissionId})
                                        urlprmsn_pay_load = urlpermission
                                        urlprmsn_res = requests.post(url+'addURLPermission', data=json.dumps(urlprmsn_pay_load), cookies = request.cookies)
                                        if urlprmsn_res.status_code == 200 and urlprmsn_res.json().get('status','') == 'OK':
                                            urlprmsn = URLPermission.query.filter_by(PermissionId = PermissionId).first()
                        usrrol = UserRole.query.filter_by(RoleId = RoleId, UserId = UserId).first()
                        if not usrrol:
                            usrrol_pay_load = {
                                'UserId':UserId,
                                'RoleId':RoleId,
                                'LastUpdateDateTime':datetime.now(),
                                'LastUpdateUserName':auth_info['Code']                                
                            }
                            UserRole(**usrrol_pay_load).add()
                            usrrol = UserRole.query.filter_by(RoleId = RoleId, UserId = UserId).first()
                        roleinfo.update({"permissions":permissionsinfo})
                        rolesinfo.append(roleinfo)
                userinfo.update({"role":rolesinfo})
                DataPermission = user.get('DataPermission').strip().lower()
                SetCode = user.get('SetCode').strip().lower()
                update_pay_load = {'id':UserId,"TableName":"UserDefine"}
                if DataPermission:
                    dtprmsn = PermissionDefine.query.filter_by(Code = DataPermission).first()
                    if not dtprmsn:
                        PermissionType = 'DATA'
                        Description = user.get('DataPermission')
                        dtprmsn_pay_load = {"Code":DataPermission,"PermissionType":PermissionType,"Description":Description}
                        dtprmsn_res = requests.post(url+'addPermission', data=json.dumps(dtprmsn_pay_load), cookies = request.cookies)
                        if dtprmsn_res.status_code == 200 and dtprmsn_res.json().get('status','') == 'OK':
                            dtprmsn = PermissionDefine.query.filter_by(Code = DataPermission).first()
                    update_pay_load.update({'DataPermission':dtprmsn.id})
                if SetCode:
                    set = SetTbl.query.filter_by(Code = SetCode).first()
                    if not set:
                        Description = user.get('SetCode')
                        set_pay_load = {"Code":SetCode,"Description":Description}
                        set_res = requests.post(url+'addSet', data=json.dumps(set_pay_load), cookies = request.cookies)
                        if set_res.status_code == 200 and set_res.json().get('status','') == 'OK':
                            set = SetTbl.query.filter_by(Code = SetCode).first()
                    update_pay_load.update({'SetId':set.id})
                update_res = requests.post(url+'updateUser', data=json.dumps(update_pay_load), cookies = request.cookies)
                if update_res.status_code == 200 and update_res.json().get('status','') == 'OK':
                    usr = UserDefine.query.filter_by(Code = UserName).first()
                userinfo.update(usr.json())
                info.append(userinfo)
        res = json.dumps({"info": info,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200        
    return Response(res, mimetype='application/json', status=status)
