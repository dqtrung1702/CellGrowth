from urllib.parse import urlsplit
from flask import session
from config import Config
import requests, json

def check_auth(url,method,cookies):
    if True:
        if "PERSON" in session:
            urls = session.get('PERSON')
            if urls:
                for u in urls:
                    if u=={"url":urlsplit(url.strip()).path.lower(),"method":method.lower()}:
                        return True,session.get('UserName')
        else:
            UAA_URL = Config.UAA_URL + "check_auth_ext"
            payload={"type":'PERSON'}
            res = requests.post(UAA_URL, data=json.dumps(payload), cookies=cookies)
            if res.json().get("status") == 'OK':
                UserName= res.json().get("data").get('UserName')
                Functions = res.json().get("data").get('Functions')
                session["PERSON"] = Functions
                session["UserName"] = UserName
                if "PERSON" in session:
                    urls = session.get('PERSON')
                    if urls:
                        for u in urls:
                            if u=={"url":urlsplit(url.strip()).path.lower(),"method":method.lower()}:
                                return True,session.get('UserName')
    return False,None