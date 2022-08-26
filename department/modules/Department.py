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
@route_dept.route('/getDEPTInfobyDEPTId',methods =['POST'])
def getDEPTInfobyDEPTId():
    if True:
        data= json.loads(request.data)
        DEPTId = data.get("id")
        deptinfo = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
        data = transf2(deptinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_dept.route('/addDEPT',methods =['POST'])
def addDEPT():
    if True:
        data = json.loads(request.data)
        itm = {}
        Code = data.get("Code","")
        if Code:            
            deptid = dept.db.department.find_one({'Code':Code},{'_id':1})
            if deptid:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)                
        else:
            res = json.dumps({'message': '"Code" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
            status = 200
            return Response(res, status=status)                    
        Active = data.get("Active",True)
        ActionCD = data.get("ReasonCD","New")
        ReasonCD = data.get("ReasonCD","New")
        EFFDT = data.get("EFFDT","")
        if EFFDT:
            try:
                EFFDT=datetime.strptime(EFFDT, "%d/%m/%Y").astimezone(pytz.utc)#save vào db giờ utc
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
        else:
            res = json.dumps({'message': '"EFFDT" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
            status = 200
            return Response(res, status=status)
        Name = data.get("Name")
        ParentId = data.get("ParentId")
        ManagerId = data.get("ManagerId")
        Description = data.get("Description")        
        auth_info = request.auth_info
        LastUpdateDateTime = datetime.now().astimezone(pytz.utc)
        LastUpdateUserName = auth_info.get('UserName','???').strip().lower()
        itm.update(
            {
                "Code":Code
                ,"Name":Name
                ,"Description":Description
                ,"Action":[
                    {
                         "EFFDT":EFFDT
                        ,'Active':Active
                        ,"ActionCD":ActionCD
                        ,"ReasonCD":ReasonCD
                        ,"ParentId":ParentId
                        ,"ManagerId":ManagerId
                    }
                ]
                ,'LastUpdateDateTime':LastUpdateDateTime
                ,'LastUpdateUserName':LastUpdateUserName
            })
        DEPTId = dept.db.department.insert_one(itm).inserted_id
        deptinfo = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
        data = transf2(deptinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, status=status)
@route_dept.route('/searchDEPT',methods =['POST'])
def searchDEPT():
    if True:
        data= json.loads(request.data)
        query = {}
        DEPTId = data.get("id","")
        if DEPTId:
            query.update({"_id":DEPTId})
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
        Description = data.get("Description")
        if Description:
            query.update({
                "Description":{
                    "$regex": Description,
                    "$options" :'i' # case-insensitive
                    }
                })

        EFFDT_F = data.get("EFFDT_F","")
        EFFDT_T = data.get("EFFDT_T","")
        EFFDT={}
        if EFFDT_F:
            try:
                EFFDT_F = datetime.strptime(EFFDT_F,'%d/%m/%Y').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            EFFDT.update({ '$gte': EFFDT_F })
        if EFFDT_T:
            try:
                EFFDT_T = datetime.strptime(EFFDT_T,'%d/%m/%Y').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            EFFDT.update({ '$lte': EFFDT_T })
        if EFFDT:
            query.update({"Action.EFFDT":EFFDT})
        
        Active = data.get("Active","")
        if Active != "":
            query.update({"Action.Active":Active})
        ActionCD = data.get("ActionCD")
        if ActionCD:
            query.update({"Action.ActionCD":ActionCD})
        ReasonCD = data.get("ReasonCD")
        if ActionCD:
            query.update({"Action.ReasonCD":ReasonCD})
        ParentId = data.get("ParentId")
        if ParentId:
            query.update({"Action.ParentId":ParentId})
        ManagerId = data.get("ManagerId")
        if ManagerId:
            query.update({"Action.ManagerId":ManagerId})        

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
def updateDEPTbyDEPTId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        itm = {}
        DEPTId = data.get('id')        
        Name = data.get("Name","")
        if Name:
            itm.update({"Name":Name})
        Description = data.get("Description","")
        if Description:
            itm.update({"Description":Description})
        data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
        dept.db.department.update_one({'Code':DEPTId}, {'$set':data})
        deptinfo = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
        data = transf2(deptinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200        
    return Response(res, mimetype='application/json', status=status)
@route_dept.route('/changeDEPTInfo',methods =['POST'])
def changeDEPTInfo():
    if True:
        data = json.loads(request.data)
        DEPTId = data.get("id","")
        EFFDT = data.get("EFFDT","")
        ActionCD = data.get("ActionCD","")
        ReasonCD = data.get("ReasonCD","")
        Active = data.get("Active","")
        ParentId = data.get("ParentId","")
        ManagerId = data.get("ManagerId","")
        auth_info = request.auth_info
        LastUpdateDateTime = datetime.now().astimezone(pytz.utc)
        LastUpdateUserName = auth_info.get('UserName','???').strip().lower()
        if DEPTId:
            try:
                EFFDT=datetime.strptime(EFFDT, "%d/%m/%Y")
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            if EFFDT:
                dept = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
                if dept:
                    maxAction = {}
                    for act in dept.get("Action"):                        
                        if act.get("EFFDT") > maxAction.get("EFFDT",datetime.strptime("01/01/1900", "%d/%m/%Y")):
                            maxAction = act
                    if maxAction.get("EFFDT",datetime.strptime("01/01/1900", "%d/%m/%Y")) < EFFDT:                            
                        EFFDT = datetime.strptime(EFFDT, "%d/%m/%Y").astimezone(pytz.utc)#save vào db giờ utc
                        if ActionCD:
                            if ReasonCD:
                                if Active == "":
                                    Active =  max.get("Active",True)
                                if not ParentId:
                                    ParentId = max.get("ParentId","")
                                if not ManagerId:
                                    ManagerId= max.get("ManagerId","")
                                dept.db.department.update_one(
                                    {'_id':ObjectId(DEPTId)},
                                    {"$set":{
                                        "LastUpdateDateTime":LastUpdateDateTime,
                                        "LastUpdateUserName":LastUpdateUserName
                                        }
                                    },
                                    {"$push":{
                                        "Action":{
                                            "EFFDT":EFFDT,
                                            "Active":Active,
                                            "ActionCD":ActionCD,
                                            "ReasonCD":ReasonCD,
                                            "ParentId":ParentId,
                                            "ManagerId":ManagerId
                                            }
                                        }
                                    })                                
                                deptinfo = dept.db.department.find_one({'_id':ObjectId(DEPTId)})
                                data = transf2(deptinfo).json_str()
                                res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
                                status = 200
                                return Response(res, status=status)
                            else:
                                res = json.dumps({'message': '"ReasonCD" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                                status = 200
                                return Response(res, status=status)
                        else:
                            res = json.dumps({'message': '"ActionCD" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                            status = 200
                            return Response(res, status=status)
                    else:
                        res = json.dumps({'message': 'EFFDT less than Maximum EFFDT of "Action" records',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                        status = 200
                        return Response(res, status=status)
                else:
                    res = json.dumps({'message': 'Data not existed',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                    status = 200
                    return Response(res, status=status)
            else:
                res = json.dumps({'message': '"EFFDT" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
        else:
            res = json.dumps({'message': '"DEPTId" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
            status = 200
            return Response(res, status=status)