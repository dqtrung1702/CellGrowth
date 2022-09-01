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
        itm={}
        auth_info = request.auth_info
        PersonId = data.get('id')
        Address ={}
        AddressType = data.get('AddressType','')
        Address1 =  data.get('Address1','')
        Address2 =  data.get('Address2','')
        ProvinceCD = data.get('ProvinceCD','')
        CityCD = data.get('CityCD','')
        CountyCD = data.get('CountyCD','')
        TownCD = data.get('TownCD','')
        DistrictCD = data.get('DistrictCD','')
        
        data = {'Address':Address,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}
        person.db.person.update_one({'_id':ObjectId(PersonId)}, {'$set':data})
        personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})
        data = transf2(personinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default)
        status = 200        
    return Response(res, mimetype='application/json', status=status)
