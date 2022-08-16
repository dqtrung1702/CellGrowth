from models.database import dept
from models.database import transf
from flask import Blueprint, request
from bson import json_util
import json
from werkzeug.wrappers import Response
from modules.common import check_auth
route_action = Blueprint('route_action', __name__)

@route_action.before_request
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
@route_action.route('/searchDEPTAction',methods =['POST'])
def searchDEPTAction():
    if True:
        data= json.loads(request.data)
        query = {"Type":"DEPT"}
        ActionId = data.get("id","")
        if ActionId:
            query.update({"_id":ActionId})
        Code = data.get("Code")
        if Code:
            query.update({"Code":Code})
        
        Name = data.get("Name")
        if Name:
            query.update({
                "Name":{
                    "$regex": Name,
                    "$options" :'i' # case-insensitive
                    }
                })        
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        actionlist = dept.db.action.find(query).sort("_id").skip(offset).limit(page_size).allow_disk_use(True)
        data = transf(actionlist).json_str()
        total_row = dept.db.action.count_documents(query)
        res = json.dumps({"data":data,'total_row':total_row,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)