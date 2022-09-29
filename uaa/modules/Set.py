from models.database import UserDefine,DataPermission,DataSet,SetTbl,DEPTSet
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
        auth_info.update({'UserName':UserName})
        setattr(request, "auth_info", auth_info)
    else:
        res = json.dumps({"message":"Access is denied","status":'FAIL'},default=json_util.default).encode('utf-8')
        status = 403
        return Response(res, mimetype='application/json', status=status)
@route_set.route('/getSetInfobySetId',methods =['POST'])
def getSetInfobySetId():
    # if True:
    #     data= json.loads(request.data)
    #     SetId = data.get("id")
    #     sql = '''select
    #                 st."id",
    #                 st."EFFFDate",
    #                 st."EFFTDate",
    #                 st."BUId",
    #                 st."Type",
    #                 st."Code" "SetCode",
    #                 st."Description",
    #                 st."LastUpdateUserName",
    #                 st."LastUpdateDateTime"
    #             from
    #                 uaa."SetTbl" st
    #             where st.id = {};'''.format(SetId)
    #     data = sqlexec(sql)
    #     res = json.dumps({"data":data.json(),"status":"OK"},default=json_util.default).encode('utf-8')
    #     status = 200
    # return Response(res, mimetype='application/json', status=status)
    if True:
        data = json.loads(request.data)
        SetId = data.get("id")
        data = SetTbl.query.get(SetId).json()
        data["SetCode"] = data.pop("Code")
        print(data)
        res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
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
        LastUpdateDateTime_F = data.get("LastUpdateDateTime_F",'')
        LastUpdateDateTime_T = data.get("LastUpdateDateTime_T",'')
        if LastUpdateDateTime_F:
            LastUpdateDateTime_F = datetime.strptime(LastUpdateDateTime_F,'%d/%m/%Y')
        if LastUpdateDateTime_T:
            LastUpdateDateTime_T = datetime.strptime(LastUpdateDateTime_T +' 23:59:59','%d/%m/%Y %H:%M:%S')
        if EFFFDate:
            EFFFDate = datetime.strptime(EFFFDate,'%d/%m/%Y')
        if EFFTDate:
            EFFTDate = datetime.strptime(EFFTDate +' 23:59:59','%d/%m/%Y %H:%M:%S')
        BUId = data.get("BUId",0)
        Type = data.get("Type",'')
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
                  and (st."EFFTDate" <= '{2}' or '{2}' = '')
                  and (st."BUId"  = {3} or {3} = 0)
                  and (st."Type"  ~ '({4})' or '{4}' = '')
                  and (st."Code"  ~ '({5})' or '{5}' = '')
                  and (st."Description"  ~ '({6})' or '{6}' = '')
                  and (st."LastUpdateUserName"  ~ '({7})' or '{7}' = '')
                  and (rd."LastUpdateDateTime" >= '{8}' or '{8}' = '')
                  and (rd."LastUpdateDateTime" <= '{9}' or '{9}' = '')
                ORDER BY rd.id
                OFFSET {10} ROWS 
                FETCH FIRST {11} ROW ONLY;'''.format(id,EFFFDate,EFFTDate,BUId,Type,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T,offset,page_size)
        sql2 = '''select sum(1) 
                from
                    uaa."SetTbl" st
                where (st.id = {0} or {0} = 0)                  
                  and (st."EFFFDate" >= '{1}' or '{1}' = '')
                  and (st."EFFTDate" <= '{2}' or '{2}' = '')
                  and (st."BUId"  = {3} or {3} = 0)
                  and (st."Type"  ~ '({4})' or '{4}' = '')
                  and (st."Code"  ~ '({5})' or '{5}' = '')
                  and (st."Description"  ~ '({6})' or '{6}' = '')
                  and (st."LastUpdateUserName"  ~ '({7})' or '{7}' = '')
                  and (rd."LastUpdateDateTime" >= '{8}' or '{8}' = '')
                  and (rd."LastUpdateDateTime" <= '{9}' or '{9}' = '');
                  '''.format(id,EFFFDate,EFFTDate,BUId,Type,Code,Description,LastUpdateUserName,LastUpdateDateTime_F,LastUpdateDateTime_T)
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
            itm = {}
            for key, value in data.items():
                    if hasattr(SetTbl, key):
                        itm.update({key:value})
            itm.update({'Code':setrcd.Code,'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()}) #update Code: role.Code để chặn không cho update Code
            setrcd.update(itm)
            data = setrcd.json()
            res = json.dumps({"data":data,"status":"OK"},default=json_util.default).encode('utf-8')
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
            dataset.remove()
        if DataPermissionIds:
            for DataPermissionId in DataPermissionIds:
                data = {'SetId':SetId, 'DataPermissionId':DataPermissionId, 'Description':Description}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
                DataSet(**data).add()
        datasets = []
        for dataset in DataSet.query.filter_by(SetId=SetId).all():
            datasets.append(dataset.json())
        res = json.dumps({"data":datasets,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
@route_set.route('/changeDEPTDataSet',methods =['POST'])
def changeDEPTDataSet():
    if True:
        data = json.loads(request.data)
        auth_info = request.auth_info
        DataPermissionIds = data.get('DataPermissionList')
        SetId = data.get('SetId')
        Description = data.get('Description','')        
        datasets= DataSet.query.filter_by(SetId=SetId).all()
        for dataset in datasets:
            dataset.remove()
        if DataPermissionIds:
            for DataPermissionId in DataPermissionIds:
                data = {'SetId':SetId, 'DataPermissionId':DataPermissionId, 'Description':Description}
                data.update({'LastUpdateDateTime':datetime.now(),'LastUpdateUserName':auth_info.get('UserName','???').strip().lower()})
                DataSet(**data).add()
        datasets = []
        for dataset in DataSet.query.filter_by(SetId=SetId).all():
            datasets.append(dataset.json())
        res = json.dumps({"data":datasets,"status":"OK"},default=json_util.default).encode('utf-8')
        status = 200
    return Response(res, mimetype='application/json', status=status)
