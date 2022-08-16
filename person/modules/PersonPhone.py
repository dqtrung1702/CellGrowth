from models.database import person
from models.database import transf,transf2
from flask import Blueprint, request
from bson import json_util
from bson.objectid import ObjectId
import json
from werkzeug.wrappers import Response
from modules.common import check_auth
from datetime import datetime
import pytz

route_phone = Blueprint('route_phone', __name__)

@route_phone.before_request
def before_request_func():
    cookies = request.cookies
    auth,UserName = check_auth(request.url,request.method,cookies)
    if auth:
        auth_info={'UserName':UserName}
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_phone.route('/updatePhonebyPersonId',methods =['POST'])
def updatePhonebyPersonId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        PersonId = data.get('id')
        Phone = data.get('Phone') #[{"PhoneType":"MOBILE","Phone":"0942585299","PRM":True}, ...]
        data = {'Phone':Phone,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}
        person.db.person.update_one({'_id':ObjectId(PersonId)}, {'$set':data})
        personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})
        data = transf2(personinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200        
    return Response(res, mimetype='application/json', status=status)
