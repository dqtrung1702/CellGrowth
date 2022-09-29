from models.database import person
from models.database import transf
from flask import Blueprint, request
from bson import json_util
from bson.objectid import ObjectId
import json
from werkzeug.wrappers import Response
from modules.common import check_auth
from datetime import datetime
import pytz

route_address = Blueprint('route_address', __name__)

@route_address.before_request
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
@route_address.route('/updateAddressbyPersonId',methods =['POST'])
def updateAddressbyPersonId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        PersonId = data.get('id','')
        Address = []
        itm = {}
        for addr in data.get('Address',''):
            AddressType = addr.get('AddressType',{})
            Address1 =  addr.get('Address1','')
            Address2 =  addr.get('Address2','')
            Province = addr.get('Province',{})
            City = addr.get('City',{})
            County = addr.get('County',{})
            Town = addr.get('Town',{})
            District = addr.get('District',{})
            Address.append({"AddressType":AddressType,"Address1":Address1,"Address2":Address2,"Province":Province,"City":City,"Town":Town,"District":District})
        itm.update({"Address":Address})
        if itm:
            itm.update({'LastUpdateDateTime':datetime.now().astimezone(pytz.utc),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})        
            person.db.person.update_one({'_id':ObjectId(PersonId)}, {'$set':itm})
            personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})
            data = transf(personinfo).jsonfobject()
            res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'Information to change is not available',"status":'FAIL'},default=json_util.default).encode('utf-8')
            status = 200
    return Response(res, mimetype='application/json', status=status)
