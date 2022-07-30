from models.database import UserDefine
from models.database import DataPermission
from models.database import DataSet
from models.database import SetTbl
from models.database import sqlexec
from flask import Blueprint, request
import jwt
from config import Config
from bson import json_util
import json
from werkzeug.wrappers import Response
from datetime import datetime
from modules.common import check_auth

route_set = Blueprint('route_set', __name__)

@route_set.before_request
def before_request_func():
    # các request tới route_user đều phải qua đây trước
    jwt_token = request.cookies.get('app_token', None)
    auth_info = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
    auth,UserName = check_auth(request.url,request.method)
    if auth:
        auth_info.update({'Username':UserName})
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_set.route('/getSetInfobySetId',methods =['POST'])
def getSetInfobySetId():
    if True:
        data= json.loads(request.data)
        SetId = data.get("id")
        
        sql = '''select
                    st."id",
                    st."EFFFDate",
                    st."EFFTDate",
                    st."BUId",
                    st."Type",
                    st."Code" "SetCode",
                    st."Description",
                    st."LastUpdateUserName",
                    st."LastUpdateDateTime"
                from
                    uaa."SetTbl" st
                where st.id = {};'''.format(SetId)
        
        data = sqlexec(sql)
        res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_set.route('/addSet',methods =['POST'])
def addSet():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        Code = data.get('Code')
        if Code:
            setrcd = SetTbl.query.filter_by(Code = Code).first()
            if not setrcd:
                payload = {}
                for key, value in data.items():
                    if hasattr(SetTbl, key):
                        payload.update({key:value})
                payload.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower(),'Code':Code})                
                SetId = SetTbl(**payload).add()
                setrcd = SetTbl.query.get(SetId)
                res = json.dumps({"data": setrcd.json(),"status":'OK'},default=json_util.default).encode('utf-8')
                status = 200
            else:
                res = json.dumps({'message': 'Data existed',"status":'FAIL'}, default=json_util.default)
                status = 200
        else:
            res = json.dumps({'message': 'Umm...',"status":'FAIL'}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_set.route('/searchSet',methods =['POST'])
def searchSet():
    if True:
        data= json.loads(request.data)
        page_size = data.get("page_size")
        page = data.get("page")
        offset = int(page)*int(page_size)-int(page_size)
        id = data.get("id",0)
        Code = data.get("Code",'')
        Description = data.get("Description",'')
        LastUpdateUserName = data.get("LastUpdateUserName",'')
        LastUpdateDateTime = data.get("LastUpdateDateTime",'')
        if LastUpdateDateTime:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime,'%d/%m/%Y')
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime+' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            LastUpdateDateTime_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            LastUpdateDateTime_T = datetime.now()
        if EFFFDate:
            EFFFDate_F = datetime.strptime(EFFFDate,'%d/%m/%Y')
            EFFFDate_T = datetime.strptime(EFFFDate +' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            EFFFDate_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            EFFFDate_T = datetime.now()
        if EFFTDate:
            EFFTDate_F = datetime.strptime(EFFTDate,'%d/%m/%Y')
            EFFTDate_T = datetime.strptime(EFFTDate +' 23:59:59','%d/%m/%Y %H:%M:%S')
        else:
            EFFTDate_F = datetime.strptime('01/01/0001','%d/%m/%Y')
            EFFTDate_T = datetime.now()
        BUId = data.get("BUId",0)
        sql = '''select
                    st."id",
                    st."EFFFDate",
                    st."EFFTDate",
                    st."BUId",
                    st."Type",
                    st."Code" "SetCode",
                    st."Description",
                    st."LastUpdateUserName",
                    st."LastUpdateDateTime"
                from
                    uaa."SetTbl" st
                where (st.id = {0} or {0} = 0)                  
                  and (st."EFFFDate" >= '{1}' or '{1}' = '')
                  and (st."EFFFDate" <= '{2}' or '{2}' = '')
                  and (st."EFFTDate" >= '{3}' or '{3}' = '')
                  and (st."EFFTDate" <= '{4}' or '{4}' = '')
                  and (st."BUId"  = {5} or {5} = 0)
                  and (st."Type"  ~ '({6})' or '{6}' = '')
                  and (st."Code"  ~ '({7})' or '{7}' = '')
                  and (st."Description"  ~ '({8})' or '{8}' = '')
                  and (st."LastUpdateUserName"  ~ '({9})' or '{9}' = '')
                  and (rd."LastUpdateDateTime" >= '{10}' or '{10}' = '')
                  and (rd."LastUpdateDateTime" <= '{11}' or '{11}' = '')
                ORDER BY rd.id
                OFFSET {12} ROWS 
                FETCH FIRST {13} ROW ONLY;'''.format(id,EFFFDate_F,EFFFDate_T,EFFTDate_F,EFFTDate_T,BUId,Type,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."SetTbl" st
                where (st.id = {0} or {0} = 0)                  
                  and (st."EFFFDate" >= '{1}' or '{1}' = '')
                  and (st."EFFFDate" <= '{2}' or '{2}' = '')
                  and (st."EFFTDate" >= '{3}' or '{3}' = '')
                  and (st."EFFTDate" <= '{4}' or '{4}' = '')
                  and (st."BUId"  = {5} or {5} = 0)
                  and (st."Type"  ~ '({6})' or '{6}' = '')
                  and (st."Code"  ~ '({7})' or '{7}' = '')
                  and (st."Description"  ~ '({8})' or '{8}' = '')
                  and (st."LastUpdateUserName"  ~ '({9})' or '{9}' = '')
                  and (rd."LastUpdateDateTime" >= '{10}' or '{10}' = '')
                  and (rd."LastUpdateDateTime" <= '{11}' or '{11}' = '');'''.format(id,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T)
        data = sqlexec(sql)
        total_row = sqlexec(sql2)
        res = json.dumps({"data":data.json(),"total_row":total_row.json(),"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_set.route('/updateSetbySetId',methods =['POST'])
def updateSetbySetId():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        SetId = data.get('id',0)
        setrcd = SetTbl.query.get(SetId)
        if setrcd:
            for key, value in data.items():
                    if hasattr(SetTbl, key):
                        data.update({key:value})
            data.update({'Code':setrcd.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update Code: role.Code để chặn không cho update Code
            setrcd.update(data)
            res = json.dumps({"data":setrcd.json(),"status":"OK"},default=json_util.default).encode('utf-8')
            status = 200
        else:
            res = json.dumps({'message': 'No data found',"status":"FAIL"}, default=json_util.default)
            status = 200
    return Response(res, mimetype='application/json', status=status)
@route_set.route('/changeUserDataSet',methods =['POST'])
def changeUserDataSet():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        DataPermissionIds = data.get('DataPermissionList')
        SetId = data.get('SetId')
        Description = data.get('Description','')        
        datasets= DataSet.query.filter_by(SetId=SetId).all()
        for dataset in datasets:
            datasets.remove()
        if DataPermissionIds:
            for DataPermissionId in DataPermissionIds:
                data = {'SetId':SetId, 'DataPermissionId':DataPermissionId, 'Description':Description}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
                DataSet(**data).add()
        datasets = []
        for dataset in DataSet.query.filter_by(UserId=UserId).all():
            datasets.append(dataset.json())
        res = json.dumps({"data":datasets,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)