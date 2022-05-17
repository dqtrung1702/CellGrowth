from config import Config
import jwt
def auth(jwt_token):
    try:
      auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
      if auth_info:
        return True
    except:
      return False

def auth_info(jwt_token):
    try:
      auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
      if auth_info:
        return True,auth_info
    except:
      return False,None
def check_url(URLList,url,**kwargs):
    for xURL in URLList:
      if xURL.get('url') == url.strip().lower():
        xlist = []
        ylist = []
        for key, value in kwargs.items():
          xlist.append(xURL.get(key))
          ylist.append(value)
        pairs = zip(xlist, ylist)
        if not any(x != y for x, y in pairs):
          return True
    return False
          
# def Pagination():
