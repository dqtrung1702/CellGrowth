from datetime import datetime
from flask import Blueprint, request,redirect,url_for,render_template,session,make_response
import requests
from config import Config
import jwt
import json
from base import check_url,auth
import base64
permission = Blueprint(
    'permission_blueprint',
    __name__,
  )
"""
Utility
"""
@permission.route('/SsoTs',methods=['GET','POST'])
def SsoTs():
    base64_template = request.values.get('template')
    base64_bytes = base64_template.encode('utf-8')
    template_bytes = base64.b64decode(base64_bytes)
    template = template_bytes.decode('utf-8')
    return template
"""
Permissions
"""
@permission.route('/Permission',methods=['GET'])
def Permission():
    jwt_token = request.cookies.get('app_token','')
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    cookies = request.cookies
    url = Config.UAA_URL
    page_size = Config.PAGE_SIZE
    data = {'page_size':page_size}
    isSearch = False
    if request.args.get('data'):
      data.update(json.loads(request.args.get('data')))
      page = data.get('page')
      isSearch = True
    else:
      page =  request.args.get('page', type=int, default=1)
      data.update({'page':page})
    res = requests.post(url+'/getPermissionList', json=data, cookies=cookies, timeout=5)  
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        if res.json().get('total_row')[0].get('sum'):
          total_row= int(res.json().get('total_row')[0].get('sum'))
        else:
          total_row = 0
        permissions = []
        for pos,line in enumerate (data):
          permissions.append({
            "id": line.get('id'),
            "STT": pos+1,
            "PermissionName": line.get('Code'),
            "PermissionType": line.get('PermissionType'),
            "Description": line.get('Description'),
            "LastUpdateDateTime": line.get('LastUpdateDateTime')
          })
        if permissions:
          total_pages = (round(total_row/page_size) + 1 if round(total_row/page_size) < (total_row/page_size) else round(total_row/page_size))
          pagination = {'page':page,'total_pages': total_pages}
          if isSearch:
            return {'permissions':permissions, 'pagination':pagination}          
          template = render_template('permission.html', title='Role', auth=True, permissions = permissions, pagination=pagination)
          template_bytes = template.encode('utf-8')
          base64_bytes = base64.b64encode(template_bytes)
          base64_template = base64_bytes.decode('utf-8')
          return template
          # return redirect(url_for('uaa_blueprint.SsoTs',template=base64_template))
        if isSearch:
          return {'users':None}
        template = render_template('role.html', title='Role', auth=True)
        return template
        # template_bytes = template.encode('utf-8')
        # base64_bytes = base64.b64encode(template_bytes)
        # base64_template = base64_bytes.decode('utf-8')
        # return redirect(url_for('uaa_blueprint.SsoTs',template=base64_template))  
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
@permission.route('/permission_detail',methods=['GET','POST'])
def permission_detail():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
        return redirect('Accessisdenied')    
    data = request.values    
    PermissionId = data.get('id')
    if request.method == 'POST':
      PermissionType = data.get('PermissionType',None)
      Description = data.get('Description',None)
      UrlListJSON = data.get('UrlListJSON')
      DataSetsJSON = data.get('DataSetsJSON')
      UrlList = []
      DataSets = []
      if UrlListJSON:
        try:
          UrlList = json.loads(UrlListJSON)
        except Exception:
          UrlList = []
      if DataSetsJSON:
        try:
          DataSets = json.loads(DataSetsJSON)
        except Exception:
          DataSets = []
      data = {}
      data.update({'Description':Description,'PermissionType':PermissionType,'UrlList':UrlList,'DataSets':DataSets})
      if PermissionId != "New":
        data.update({'PermissionId':PermissionId})
        res = requests.post(url+'/updatePermission', json=data, cookies=cookies, timeout=5)
      else:        
        Code = data.get('PermissionName',None)
        data.update({'Code':Code})
        res = requests.post(url+'/addPermission', json=data, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')
         
    if PermissionId !='New':
      '''permission'''
      res = requests.post(url+'/getPermissionInfo', json={'ids':[PermissionId]}, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data = res.json().get('data')
          permission = res.json().get('data')[0]
          permissions = [{'id':permission.get('id'),'text':permission.get('PermissionName')}]
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
      '''url'''
      data = {'PermissionId' : PermissionId}
      res = requests.post(url+'/getURLbyPermission', json=data, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
          urlpermission = []
          for pos,line in enumerate (data):
            linedata = {"STT":pos+1}
            linedata.update(line)
            urlpermission.append(linedata)
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
    else:
      permission = {}
      urlpermission = []
    return render_template('permissiondetail.html', title='Permission', auth=True, permission = permission, urlpermission = urlpermission)
@permission.route('/getURLbyPermission',methods=['GET', 'POST'])
def getURLbyPermission():
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    cookies = request.cookies
    url = Config.UAA_URL
    data = json.loads(request.data)
    PermissionId = data.get('PermissionId')
    data = {'PermissionId' : PermissionId}
    res = requests.post(url+'/getURLbyPermission', json=data, cookies=cookies, timeout=5)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        urlpermission = []
        for pos,line in enumerate (data):
          linedata = {"STT":pos+1}
          linedata.update(line)
          urlpermission.append(linedata)
        return json.dumps(urlpermission)
    elif res.status_code == 403:
      return redirect('Accessisdenied')
    else:
      return redirect('home')
@permission.route('/permission_searching',methods=['GET','POST'])
def permission_searching():
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    data = {}
    data.update(json.loads(request.data.decode('utf-8')))
    return redirect(url_for('permission_blueprint.Permission',data = json.dumps(data)))
@permission.route('/permission_deletion',methods=['GET','POST'])
def permission_deletion():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
      return redirect('Accessisdenied')    
    data = request.values
    PermissionId = data.get('id')
    data = {'id':PermissionId}
    res = requests.post(url+'/deletePermissionById', json=data, cookies=cookies, timeout=5)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
    return redirect(url_for('permission_blueprint.Permission'))
"""
select2
"""
@permission.route('/getDataPermissionList',methods=['POST'])
def getDataPermissionList():
  cookies = request.cookies
  jwt_token = cookies.get('app_token','')
  xauth = auth(jwt_token)
  if not xauth:
    return redirect('Accessisdenied')    
  url = Config.UAA_URL
  data = json.loads(request.data.decode('utf-8'))
  page = data.get('page',1)
  Code = data.get('Code')
  data = {'Code':Code,'PermissionType':'DATA','page':page,'page_size' : 10}
  res = requests.post(url+'/getDataPermissionList', json=data, cookies=cookies, timeout=5)
  if res.status_code == 200:
    if res.json().get('status','') == 'OK':
      data= res.json().get('data')
      datapermissions = []
      for d in data:
        datapermissions.append({"id":d.get("id"),"text":d.get("Code")})
      datapermissions = list({v['id']:v for v in datapermissions}.values())
      return json.dumps(datapermissions)
@permission.route('/getRolePermissionList',methods=['POST'])
def getRolePermissionList():
  cookies = request.cookies
  jwt_token = cookies.get('app_token','')
  xauth = auth(jwt_token)
  if not xauth:
    return redirect('Accessisdenied')    
  url = Config.UAA_URL
  data = json.loads(request.data.decode('utf-8'))
  page = data.get('page',1)
  Code = data.get('Code')
  data = {'Code':Code,'PermissionType':'ROLE','page' : page,'page_size' : Config.PAGE_SIZE}
  res = requests.post(url+'/getRolePermissionList', json=data, cookies=cookies, timeout=5)
  if res.status_code == 200:
    if res.json().get('status','') == 'OK':
      data= res.json().get('data') 
      permissions = []
      for d in data:
        permissions.append({"id":d.get("id"),"text":d.get("Code")})
      permissions = list({v['id']:v for v in permissions}.values())
      return json.dumps(permissions)
