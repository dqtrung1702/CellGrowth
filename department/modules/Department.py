from models.database import dept
from models.database import transf,transf2
from flask import Blueprint, request
from bson import json_util
from bson.objectid import ObjectId
import json
from werkzeug.wrappers import Response
from modules.common import check_auth
from datetime import datetime
import pytz

route_dept = Blueprint('route_dept', __name__)

@route_dept.before_request
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
@route_dept.route('/getDEPTInfobyDEPTCode',methods =['POST'])
def getDEPTInfobyDEPTId():
    if True:
        data= json.loads(request.data)
        DEPTCode = data.get("Code")
        deptinfo = dept.db.department.find_one({'Code':DEPTCode})
        data = transf2(deptinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_dept.route('/addDEPT',methods =['POST'])
def addDEPT():
    if True:
        data = json.loads(request.data)
        if "Code" in data:
            Code = data.get("Code")
        EFFDT = datetime.strptime(data.get("EFFDT"), "%d/%m/%Y").astimezone(pytz.utc)#save vào db giờ utc
        Status = data.get("Status")
        ActionCD = data.get("ActionCD")
        Name = data.get("Name")
        ParentId = data.get("ParentId")
        ManagerId = data.get("ManagerId")
        Description = data.get("Description")
        
        auth_info = request.auth_info
        LastUpdateDateTime = datetime.now().astimezone(pytz.utc)
        LastUpdateUserName = auth_info.get('UserName','???').strip().lower()
        DEPTId = dept.db.department.insert_one({
            'Code':Code,
            'EFFDT':EFFDT,
            'Status':Status,
            'ActionCD':ActionCD,
            'Name':Name,
            'ParentId':ParentId,
            'ManagerId': ManagerId,
            'Description':Description,
            'LastUpdateDateTime':LastUpdateDateTime,
            'LastUpdateUserName':LastUpdateUserName
        }).inserted_id
        deptinfo = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
        data = transf2(deptinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, status=status)
@route_dept.route('/searchDEPT',methods =['POST'])
def searchDEPT():
    if True:
        data= json.loads(request.data)
        auth_info = request.auth_info
        query = {}
        DEPTId = data.get("id","")
        if DEPTId:
            query.update({"_id":DEPTId})
        Code = data.get("Code")
        if Code:
            query.update({"Code":Code})
        EFFDT_F = data.get("EFFDT_F","")
        EFFDT_T = data.get("EFFDT_T","")
        EFFDT={}
        if EFFDT_F:
            EFFDT_F = datetime.strptime(EFFDT_F,'%d/%m/%Y').astimezone(pytz.utc)
            EFFDT.update({ '$gte': EFFDT_F })
        if EFFDT_T:
            EFFDT_T = datetime.strptime(EFFDT_T +' 23:59:59','%d/%m/%Y %H:%M:%S').astimezone(pytz.utc)
            EFFDT.update({ '$lte': EFFDT_T })
        if EFFDT:
            query.update({"EFFDT":EFFDT})

        Status = data.get("Status")
        if Status:
            query.update({"Status":Status})
        ActionCD = data.get("ActionCD")
        if ActionCD:
            query.update({"ActionCD":ActionCD})
        Name = data.get("Name")
        if Name:
            query.update({
                "Name":{
                    "$regex": Name,
                    "$options" :'i' # case-insensitive
                    }
                })
        ParentId = data.get("ParentId")
        if ParentId:
            query.update({"ParentId":ParentId})
        ManagerId = data.get("ManagerId")
        if ManagerId:
            query.update({"ManagerId":ManagerId})
        Description = data.get("Description")
        if Description:
            query.update({
                "Description":{
                    "$regex": Description,
                    "$options" :'i' # case-insensitive
                    }
                })
        LastUpdateUserName = data.get("LastUpdateUserName")
        if LastUpdateUserName:
            query.update({"LastUpdateUserName":LastUpdateUserName})
        LastUpdateDateTime_F = data.get("LastUpdateDateTime_F",'')
        LastUpdateDateTime_T = data.get("LastUpdateDateTime_T",'')
        LastUpdateDateTime={}
        if LastUpdateDateTime_F:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime_F,'%d/%m/%Y').astimezone(pytz.utc)
            LastUpdateDateTime.update({ '$gte': LastUpdateDateTime_F })
        if LastUpdateDateTime_T:
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime_T +' 23:59:59','%d/%m/%Y %H:%M:%S').astimezone(pytz.utc)
            LastUpdateDateTime.update({ '$lte': LastUpdateDateTime_T })
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        deptlist = dept.db.department.find(query).sort("_id").skip(offset).limit(page_size).allow_disk_use(True)
        data = transf(deptlist).json_str()
        total_row = dept.db.department.count_documents(query)
        res = json.dumps({"data":data,'total_row':total_row,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_dept.route('/updateDEPTbyDEPTId',methods =['POST'])
def updateDEPTbyDEPTCode():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        DEPTCode = data.get('Code')
        data.pop('id')
        data.pop('Code')
        EFFDT = data.get("EFFDT","")
        if EFFDT:
            data.pop("EFFDT")
            data.update({"EFFDT":datetime.strptime(EFFDT, "%d/%m/%Y").astimezone(pytz.utc)})
        data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
        dept.db.department.update_one({'Code':DEPTCode}, {'$set':data})
        deptinfo = dept.db.department.find_one({'Code':DEPTCode})
        data = transf2(deptinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200        
    return Response(res, mimetype='application/json', status=status)