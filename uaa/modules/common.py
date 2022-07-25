from models.database import sqlexec
import json
from bcrypt import hashpw, checkpw, gensalt
from urllib.parse import urlsplit

def hashed_password(Password):
    return hashpw(Password.encode('utf-8'), gensalt())

def check_password(hashPassword:bytes, Password:str):
    return checkpw(Password.encode('utf-8'),hashPassword) 

def check_userurl(UserId,url,method,type):
    url = urlsplit(url.strip().lower())
    print(url.path,method,type,UserId)
    if True:
        sql = '''select
                    1
                from uaa."UserRole" ur
                join uaa."RolePermission" rp on
                    rp."RoleId" = ur."RoleId"
                join uaa."URLPermission" up on
                    up."PermissionId" = rp."PermissionId" 
                and up."url" = '{}'
                and up."Method" = '{}'
                and up."Type" = '{}'              
                where ur."UserId" = {}
                limit 1;'''.format(url.path,method,type,UserId)
        data = sqlexec(sql).json()
        print('data',data)
        if data:
            return True
    return False