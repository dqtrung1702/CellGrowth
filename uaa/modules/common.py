from models.database import sqlexec
import json
from bcrypt import hashpw, checkpw, gensalt
from urllib.parse import urlsplit

def hashed_password(Password):
    return hashpw(Password.encode('utf-8'), gensalt())

def check_password(hashPassword:bytes, Password:str):
    return checkpw(Password.encode('utf-8'),hashPassword) 

def check_auth(UserId,url,method,type):
    url = urlsplit(url.strip().lower())
    if True:
        if url.path == '/check_auth_ext':
            return True,None
        sql = '''select
                    ud."UserName"
                from uaa."UserDefine" ud 
                join uaa."UserRole" ur on
                    ur."UserId" = ud."id"
                join uaa."RolePermission" rp on
                    rp."RoleId" = ur."RoleId"
                join uaa."URLPermission" up on
                    up."PermissionId" = rp."PermissionId" 
                and up."url" = '{}'
                and up."Method" = '{}'
                and up."Type" = '{}'              
                where ur."id" = {}
                limit 1;'''.format(url.path,method,type,UserId)
        data = sqlexec(sql).json()
        if data:
            return True,data.get('UserName')        
    return False,None