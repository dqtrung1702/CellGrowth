from models.database import sqlexec
import json
from bcrypt import hashpw, checkpw, gensalt
from urllib.parse import urlsplit

def hashed_password(Password):
    return hashpw(Password.encode('utf-8'), gensalt())

def check_password(hashPassword:bytes, Password:str):
    return checkpw(Password.encode('utf-8'),hashPassword) 

def check_userurl(UserId,url,type,*method):
    
    url = urlsplit(url.strip().lower())
    print(url)
    print(method)
    if True:
        sql = '''select
                    1
                from
                    uaa."UserDefine" ud
                join uaa."UserRole" ur on
                    ur."UserId" = ud.id
                join uaa."RolePermission" rp on
                    rp."RoleId" = ur."RoleId"
                join uaa."URLPermission" up on
                    up."PermissionId" = rp."PermissionId" 
                and up."url" = '{}'
                and up."Type" = {}                
                where ud.id = {}
                limit 1;'''.format(url.path,type,UserId)
        data = sqlexec(sql)
        if data:
            return True
    return True