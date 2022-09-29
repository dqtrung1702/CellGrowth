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
        data = transf(personinfo).jsonfobject()
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
        else:
            res = json.dumps({'message': '"Code" is required',"status":'FAIL'}, default=json_util.default).encode('utf-8')
            status = 200
            return Response(res, status=status)
        BirthDate = data.get("BirthDate","")
        if BirthDate:
            try:
                BirthDate = datetime.strptime(BirthDate, "%d/%m/%Y").astimezone(pytz.utc)#save vào db giờ utc
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)        
        BirthPlace = data.get("BirthPlace","")
        BirthCity = data.get("BirthCity",{})
        Nationallity = data.get("Nationallity",{})
        FamilyType = data.get("FamilyType","")
        Ethenic = data.get("Ethenic",{})
        FullName = data.get("FullName","")
        LastUpdateDateTime = datetime.now().astimezone(pytz.utc)
        auth_info = request.auth_info
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
        data = transf(personinfo).jsonfobject()
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
            try:
                BirthDate_F = datetime.strptime(BirthDate_F,'%d/%m/%Y').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            BirthDate.update({ '$gte': BirthDate_F })
        if BirthDate_T:
            try:
                BirthDate_T = datetime.strptime(BirthDate_T +' 23:59:59','%d/%m/%Y %H:%M:%S').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            BirthDate.update({ '$lte': BirthDate_T })
        if BirthDate:
            query.update({"BirthDate":BirthDate})
        BirthPlace = data.get("BirthPlace","")
        if BirthPlace:
            query.update({
                "BirthPlace":{
                    "$regex": BirthPlace,
                    "$options" :'i' # case-insensitive
                    }
                })
        BirthCity = data.get("BirthCity",{}).get("Code","")
        if BirthCity:
            query.update({"BirthCity.Code":BirthCity})
        Nationallity = data.get("Nationallity",{}).get("Code","")
        if Nationallity:
            query.update({"Nationallity.Code":Nationallity})
        FamilyType = data.get("FamilyType","")
        if FamilyType:
            query.update({
                "FamilyType":{
                    "$regex": FamilyType,
                    "$options" :'i' # case-insensitive
                    }
                })
        Ethenic = data.get("Ethenic",{}).get("Code","")
        if Ethenic:
            query.update({"Ethenic.Code":Ethenic})
        FullName = data.get("FullName","")
        if FullName:
            query.update({
                "FullName":{
                    "$regex": FullName,
                    "$options" :'i' # case-insensitive
                    }
                })
        LastUpdateUserName = data.get("LastUpdateUserName","")
        if LastUpdateUserName:
            query.update({
                "LastUpdateUserName":{
                    "$regex": LastUpdateUserName,
                    "$options" :'i' # case-insensitive
                    }
                })
        LastUpdateDateTime_F = data.get("LastUpdateDateTime_F",'')
        LastUpdateDateTime_T = data.get("LastUpdateDateTime_T",'')
        LastUpdateDateTime={}
        if LastUpdateDateTime_F:
            try:
                LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime_F,'%d/%m/%Y').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            LastUpdateDateTime.update({ '$gte': LastUpdateDateTime_F })
        if LastUpdateDateTime_T:
            try:
                LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime_T +' 23:59:59','%d/%m/%Y %H:%M:%S').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            LastUpdateDateTime.update({ '$lte': LastUpdateDateTime_T })            
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        personlist = person.db.person.find(query).sort("_id").skip(offset).limit(page_size).allow_disk_use(True)
        data = transf(personlist).jsonfobject()
        total_row = person.db.person.count_documents(query)
        res = json.dumps({"data":data,'total_row':total_row,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_basic.route('/updatePersonbyPersonId',methods =['POST'])
def updatePersonbyPersonId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        PersonId = data.get('id','')
        itm={}
        BirthDate = data.get("BirthDate","")
        if BirthDate:
            try:
                BirthDate = datetime.strptime(BirthDate,'%d/%m/%Y').astimezone(pytz.utc)
            except ValueError as e:
                res = json.dumps({'message': e,"status":'FAIL'}, default=json_util.default).encode('utf-8')
                status = 200
                return Response(res, status=status)
            itm.update({"BirthDate":BirthDate})
        BirthPlace = data.get("BirthPlace","")
        if BirthPlace:
            itm.update({"BirthPlace":BirthPlace})
        BirthCity = data.get("BirthCity",{})
        if BirthCity:
            itm.update({"BirthCity":BirthCity})
        Nationallity = data.get("Nationallity",{})
        if Nationallity:
            itm.update({"Nationallity":Nationallity})
        FamilyType = data.get("FamilyType","")
        if FamilyType:
            itm.update({"FamilyType":FamilyType})
        Ethenic = data.get("Ethenic",{})
        if Ethenic:
            itm.update({"Ethenic":Ethenic})
        FullName = data.get("FullName","")
        if FullName:
            itm.update({"FullName":FullName})        
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