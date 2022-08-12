from urllib.parse import urlsplit
from flask import session
from config import Config
import requests, json

def check_auth(url,method,cookies):
    if True:
        if "DEPT" in session:
            urls = session.get('DEPT')
            if urls:
                for u in urls:
                    if u=={"url":urlsplit(url.strip()).path.lower(),"method":method.lower()}:
                        return True,session.get('UserName')
        else:
            UAA_URL = Config.UAA_URL + "check_auth_ext"
            payload={"type":'DEPT'}
            res = requests.post(UAA_URL, data=json.dumps(payload), cookies=cookies)
            UserName= res.json().get("data").get('UserName')
            Functions = res.json().get("data").get('Functions')
            session["DEPT"] = Functions
            session["UserName"] = UserName
            if "DEPT" in session:
                urls = session.get('DEPT')
                if urls:
                    for u in urls:
                        if u=={"url":urlsplit(url.strip()).path.lower(),"method":method.lower()}:
                            return True,session.get('UserName')
    return False,None