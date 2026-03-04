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

route_email = Blueprint('route_email', __name__)

@route_email.before_request
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
@route_email.route('/updateEmailbyPersonId',methods =['POST'])
def updateEmailbyPersonId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        PersonId = data.get('id','')
        Email = data.get('Email','') #[{"Email":"abc@x.com","PRM":True}, ...]
        if not Email:
            res = json.dumps({'message': '"Email" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
            status = 200
            return Response(res, status=status)

        payload = {'Email':Email,'LastUpdateDateTime':datetime.now().astimezone(pytz.utc),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}
        person.db.person.update_one({'_id':ObjectId(PersonId)}, {'$set':payload})
        personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})
        data = transf2(personinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default)
        status = 200
        return Response(res, mimetype='application/json', status=status)
