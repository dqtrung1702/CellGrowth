from urllib.parse import urlsplit
from flask import session
from config import Config
import requests, json

def check_auth(url,method,cookies):
    if True:
        urls = session.get('PERSON','')
        if urls:
            if {"url":urlsplit(url.strip()).path.lower(),"method":method.lower()} in urls:
                return True,session.get('UserName')
        else:
            UAA_URL = Config.UAA_URL + "check_auth_ext"
            payload={"type":'PERSON'}
            res = requests.post(UAA_URL, data=json.dumps(payload), cookies=cookies)
            if ("status","OK") in res.json().items():
                UserName= res.json().get("data").get('UserName')
                Functions = res.json().get("data").get('Functions')
                session["PERSON"] = Functions
                session["UserName"] = UserName
                urls = session.get('PERSON','')
                if urls:
                    if {"url":urlsplit(url.strip()).path.lower(),"method":method.lower()} in urls:
                        return True,session.get('UserName')
    return False,None