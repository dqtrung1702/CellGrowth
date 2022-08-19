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

route_basic = Blueprint('route_basic', __name__)

@route_basic.before_request
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
@route_basic.route('/getPersonInfobyPersonId',methods =['POST'])
def getPersonInfobyPersonId():
    if True:
        data= json.loads(request.data)
        PersonId = data.get("id")
        personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})
        data = transf2(personinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_basic.route('/addPerson',methods =['POST'])
def addPerson():
    if True:
        data = json.loads(request.data)
        Code = data.get("Code")
        if Code:
            PersonId = person.db.person.find_one({'Code':Code},{'_id':1})
            if PersonId:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
        auth_info = request.auth_info
        BirthDate = datetime.strptime(data.get("BirthDate"), "%d/%m/%Y").astimezone(pytz.utc)#save vào db giờ utc
        BirthPlace = data.get("BirthPlace")
        BirthCity = data.get("BirthCity")
        Nationallity = data.get("Nationallity")
        FamilyType = data.get("FamilyType")
        Ethenic = data.get("Ethenic")
        FullName = data.get("FullName")
        LastUpdateDateTime = datetime.now().astimezone(pytz.utc)
        LastUpdateUserName = auth_info.get('UserName','???').strip().lower()
        PersonId = person.db.person.insert_one({
            'Code':Code,
            'BirthDate':BirthDate,
            'BirthPlace':BirthPlace,
            'BirthCity':BirthCity,
            'Nationallity':Nationallity,
            'FamilyType':FamilyType,
            'Ethenic': Ethenic,
            'FullName':FullName,
            'LastUpdateDateTime':LastUpdateDateTime,
            'LastUpdateUserName':LastUpdateUserName
        }).inserted_id
        personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})        
        data = transf2(personinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, status=status)
@route_basic.route('/searchPerson',methods =['POST'])
def searchPerson():
    if True:
        data= json.loads(request.data)
        query = {}
        PersonId = data.get("id","")
        if PersonId:
            query.update({"_id":PersonId})
        Code = data.get("Code")
        if Code:
            query.update({"Code":Code})
        BirthDate_F = data.get("BirthDate_F","")
        BirthDate_T = data.get("BirthDate_T","")
        BirthDate={}
        if BirthDate_F:
            BirthDate_F = datetime.strptime(BirthDate_F,'%d/%m/%Y').astimezone(pytz.utc)
            BirthDate.update({ '$gte': BirthDate_F })
        if BirthDate_T:
            BirthDate_T = datetime.strptime(BirthDate_T +' 23:59:59','%d/%m/%Y %H:%M:%S').astimezone(pytz.utc)
            BirthDate.update({ '$lte': BirthDate_T })
        if BirthDate:
            query.update({"BirthDate":BirthDate})
        BirthPlace = data.get("BirthPlace")
        if BirthPlace:
            query.update({
                "BirthPlace":{
                    "$regex": BirthPlace,
                    "$options" :'i' # case-insensitive
                    }
                })
        BirthCity = data.get("BirthCity.Code")
        if BirthCity:
            query.update({"BirthCity.Code":BirthCity})
        Nationallity = data.get("Nationallity.Code")
        if Nationallity:
            query.update({"Nationallity.Code":Nationallity})
        FamilyType = data.get("FamilyType")
        if FamilyType:
            query.update({"FamilyType":FamilyType})
        Ethenic = data.get("Ethenic.Code")
        if Ethenic:
            query.update({"Ethenic.Code":Ethenic})
        FullName = data.get("FullName")
        if FullName:
            query.update({
                "FullName":{
                    "$regex": FullName,
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
        personlist = person.db.person.find(query).sort("_id").skip(offset).limit(page_size).allow_disk_use(True)
        data = transf(personlist).json_str()
        total_row = person.db.person.count_documents(query)
        res = json.dumps({"data":data,'total_row':total_row,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_basic.route('/updatePersonbyPersonId',methods =['POST'])
def updatePersonbyPersonId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        PersonId = data.get('id')
        data.pop('id')
        data.pop('Code')
        BirthDate = data.get("BirthDate","")
        if BirthDate:
            data.pop("BirthDate")
            data.update({"BirthDate":datetime.strptime(BirthDate, "%d/%m/%Y").astimezone(pytz.utc)})
        data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
        person.db.person.update_one({'_id':ObjectId(PersonId)}, {'$set':data})
        personinfo = person.db.person.find_one({'_id':ObjectId(PersonId)})
        data = transf2(personinfo).json_str()
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)