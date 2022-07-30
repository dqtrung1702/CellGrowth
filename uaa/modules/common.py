from bcrypt import hashpw, checkpw, gensalt
from urllib.parse import urlsplit
from flask import session
from models.database import sqlexec

def hashed_password(Password):
    return hashpw(Password.encode('utf-8'), gensalt())

def check_password(hashPassword:bytes, Password:str):
    return checkpw(Password.encode('utf-8'),hashPassword) 

def check_auth(url,method): 
    print(session)   
    if True:
        url = urlsplit(url.strip().lower())
        urls = session.get('UAA')
        if urls:
            for u in urls:
                if u=={"url":url.path.lower(),"method":method.lower()}:
                    return True,session.get('UserName')
    return False,None

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
        Pages = [page.get('url') for page in sqlexec(sql).json()]
    return Pages
def getFunctionbyUserId(UserId,Type):
    if True:
        sql = '''select
                    url, up."Method"
                from
                    uaa."UserRole" ur
                join uaa."RolePermission" rp on
                    rp."RoleId" = ur."RoleId"
                join uaa."URLPermission" up on
                    up."PermissionId" = rp."PermissionId"
                    and up."Type" = '{1}'
                where ur."UserId" = {0};'''.format(UserId,Type)
        Functions = [{"method":function.get('Method').lower(),"url":function.get('url').lower()} for function in sqlexec(sql).json()]
    return Functions