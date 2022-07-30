from urllib.parse import urlsplit
from flask import session
from config import Config
import requests, json

def check_auth(url,method,cookies):
    url = urlsplit(url.strip().lower())
    if "Functions" in session:
        urls = session.get('Functions')
        if urls:
            for u in urls:
                if u=={"url":url.path.lower(),"method":method.lower()}:
                    return True,session.get('UserName')
    else:
        url = Config.UAA_URL + "check_auth_ext"
        payload={"url":url,"method":method,"type":'DEPT'}
        res = requests.post(url, data=json.dumps(payload), cookies=cookies)
        UserName= res.json().get("data").get('UserName')
        Functions = res.json().get("data").get('Functions')
        session["Functions"] = Functions
        session["UserName"] = UserName
        if "Functions" in session:
            check_auth(url,method,cookies)
    return False,None