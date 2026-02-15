from datetime import datetime
from flask import Blueprint, request,redirect,url_for,render_template,session,make_response
import requests
from config import Config
import jwt
import json
from base import check_url,auth
import base64
role = Blueprint(
    'role_blueprint',
    __name__,
  )
"""
Utility
"""
@role.route('/SsoTs',methods=['GET','POST'])
def SsoTs():
    base64_template = request.values.get('template')
    base64_bytes = base64_template.encode('utf-8')
    template_bytes = base64.b64decode(base64_bytes)
    template = template_bytes.decode('utf-8')
    return template
"""
Roles
"""
@role.route('/Role',methods=['GET','POST'])
def Role():
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
    res = requests.post(url+'/getRoleList', json=data, cookies=cookies, timeout=5)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        if res.json().get('total_row')[0].get('sum'):
          total_row= int(res.json().get('total_row')[0].get('sum'))
        else:
          total_row = 0
        roles = []
        for pos,line in enumerate (data):
          roles.append({
            "id": line.get('id'),
            "STT": pos+1,
            "RoleName": line.get('Code'),
            "Description": line.get('Description'),
            "LastUpdateDateTime": line.get('LastUpdateDateTime')
          })
        if roles:
          total_pages = (round(total_row/page_size) + 1 if round(total_row/page_size) < (total_row/page_size) else round(total_row/page_size))
          pagination = {'page':page,'total_pages': total_pages}
          if isSearch:
            return {'roles':roles, 'pagination':pagination}          
          template = render_template('role.html', title='Role', auth=True, roles = roles, pagination=pagination)
          template_bytes = template.encode('utf-8')
          base64_bytes = base64.b64encode(template_bytes)
          base64_template = base64_bytes.decode('utf-8')
          # return template
          return redirect(url_for('role_blueprint.SsoTs',template=base64_template))
        if isSearch:
          return {'users':None}
        template = render_template('role.html', title='Role', auth=True)
        template_bytes = template.encode('utf-8')
        base64_bytes = base64.b64encode(template_bytes)
        base64_template = base64_bytes.decode('utf-8')
        return redirect(url_for('role_blueprint.SsoTs',template=base64_template))
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
@role.route('/role_searching',methods=['GET','POST'])
def role_searching():
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    data = {}
    data.update(json.loads(request.data.decode('utf-8')))
    return redirect(url_for('role_blueprint.Role',data = json.dumps(data)))
@role.route('/getUserByRole',methods=['GET','POST'])
def getUserByRole():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
      return redirect('Accessisdenied')    
    data = json.loads(request.data.decode('utf-8'))
    RoleId = data.get('id')
    data = {'id':RoleId}
    res = requests.post(url+'/getUserByRole', data=json.dumps(data), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        userlist = []
        for d in data:
          userlist.append(d.get('UserName'))
        if userlist:
          return 'List of users who will lose this role:\n-' + '\n-'.join(userlist) + '\nAre you sure?'
        return 'Are you sure?'
@role.route('/getRoleByPermission',methods=['GET','POST'])
def getRoleByPermission():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
      return redirect('Accessisdenied')    
    data = json.loads(request.data.decode('utf-8'))
    PermissionId = data.get('id')
    data = {'id':PermissionId}
    res = requests.post(url+'/getRoleByPermission', data=json.dumps(data), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        rolelist = []
        for d in data:
          rolelist.append(d.get('RoleName'))
        if rolelist:
          return 'List of roles which will lose this permission:\n-' + '\n-'.join(rolelist) + '\nAre you sure?'
        return 'Are you sure?'
@role.route('/role_deletion',methods=['GET','POST'])
def role_deletion():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
      return redirect('Accessisdenied')    
    data = request.values
    RoleId = data.get('id')
    data = {'id':RoleId}
    res = requests.post(url+'/deleteRoleById', data=json.dumps(data), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
    return redirect(url_for('role_blueprint.Role'))
@role.route('/role_detail',methods=['GET','POST'])
def role_detail():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
        return redirect('Accessisdenied')    
    data = request.values
    RoleId = data.get('id')
    if request.method == 'POST':
      Description = data.get('Description',None)
      Permission = data.getlist('Permission',None)
      data = {}
      data.update({'Description':Description,'Permission':Permission})
      if RoleId != "New":
        data.update({'RoleId':RoleId})
        res = requests.post(url+'/updateRole', json=data, cookies=cookies, timeout=5)
      else:        
        Code = data.get('RoleName',None)
        data.update({'Code':Code})
        res = requests.post(url+'/addRole', json=data, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
          if RoleId == "New":
            return redirect(url_for('role_blueprint.Role'))
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')      
      return redirect(url_for('role_blueprint.role_detail', id = RoleId))
    '''role'''
    if RoleId != 'New':    
      res = requests.post(url+'/getRoleInfo', json={'id':RoleId}, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          role = res.json().get('data')[0]
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
      '''rolepermission'''
      res = requests.post(url+'/getPermissionByRole', json={'id':RoleId}, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          permission = res.json().get('data')
          permissions = []
          for p in permission:
            permissions.append({'id':p.get('PermissionId'),'text':p.get('PermissionName')})    
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
    else:
      role = {}
      permissions = []
    return (render_template('roledetail.html', title='Role', auth=True, role = role, permissions = permissions))
"""
select2
"""
@role.route('/getRoleList',methods=['POST'])
def getRoleList():
  cookies = request.cookies
  jwt_token = cookies.get('app_token','')
  xauth = auth(jwt_token)
  if not xauth:
    return redirect('Accessisdenied')
  url = Config.UAA_URL
  data = json.loads(request.data.decode('utf-8'))
  page = data.get('page',1)
  Code = data.get('Code')
  data = {'Code':Code,'page' : page,'page_size' : Config.PAGE_SIZE}
  res = requests.post(url+'/getRoleList', data=json.dumps(data), cookies=cookies)
  if res.status_code == 200:
    if res.json().get('status','') == 'OK':
      data= res.json().get('data') 
      roles = []
      for d in data:
        roles.append({"id":d.get("id"),"text":d.get("Code")})      
      roles = list({v['id']:v for v in roles}.values())
      return json.dumps(roles)
