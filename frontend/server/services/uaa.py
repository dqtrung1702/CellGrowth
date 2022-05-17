from datetime import datetime
from flask import Blueprint, request,redirect,url_for,render_template,session,make_response
import requests
from config import Config
import jwt
import json
from base import check_url,auth
import base64
uaa = Blueprint(
    'uaa_blueprint',
    __name__,
  )
"""
Utility
"""
@uaa.route('/SsoTs',methods=['GET','POST'])
def SsoTs():
    base64_template = request.values.get('template')
    base64_bytes = base64_template.encode('utf-8')
    template_bytes = base64.b64decode(base64_bytes)
    template = template_bytes.decode('utf-8')
    return template


"""
Auth
"""
@uaa.route('/Accessisdenied')
def Accessisdenied():
  return render_template('base.html', title='ERROR:Access is denied', auth=True)
  
# @uaa.route('/login',methods=['GET', 'POST'])
# def login():
#     if 'URLList' in session:
#       session.pop('URLList',None)
#     jwt_token = request.cookies.get('app_token','')  
#     xauth = auth(jwt_token)
#     if xauth:
#       return redirect(url_for('home_blueprint.home'))
#     else:
#       if request.method == 'POST':
#         data = request.form
#         url = Config.UAA_URL
#         payload={'UserName': data.get('username'),'Password': data.get('password')}
#         resp = redirect(url_for('home_blueprint.home'))
#         res = requests.post(url  + '/login', headers = {}, data=json.dumps(payload))
#         if res.status_code == 200:
#           if res.json().get('status','') == 'OK':
#             jwt_token = res.json().get('token','')            
#           else:
#             return render_template('login.html', title='Error', error=res.json(), auth=False)
#         else:
#           return render_template('login.html', title='Error', error=res.json(), auth=False)
#         resp.set_cookie('app_token', res.json().get('token'))
#         return resp
#       else:
#         return render_template('login.html', title='Login', auth=False)

@uaa.route('/logout')
def logout():
  resp = redirect(url_for('home_blueprint.home'))
  resp.delete_cookie('app_token')
  return resp

@uaa.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      data = request.form
      url = Config.UAA_URL + '/register'
      payload={'Code': data.get('username'),'Password': data.get('password'), 'NameDisplay': data.get('namedisplay')}
      res = requests.post(url, headers = {}, data=json.dumps(payload))
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          jwt_token = res.json().get('token','')
          resp = redirect(url_for('home_blueprint.home'))
          resp.set_cookie('app_token', jwt_token)
          return resp
        else:
          return render_template('register.html', title='Error', error=res.text, auth=False)
      else:
        return render_template('register.html', title='Error', error=res.text, auth=False)
    else:
      return render_template('register.html', title='Register', auth=False)

"""
Users
"""
@uaa.route('/User',methods=['GET','POST'])
def User():
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    cookies = request.cookies
    url = Config.UAA_URL
    data = {} 
    page_size = Config.PAGE_SIZE
    page =  request.args.get('page', type=int, default=1)
    data.update({'page' : page,'page_size' : page_size})
    isSearch = False
    if request.data:      
      data.update(json.loads(request.data.decode('utf-8')))
      page = data.get('page')
      isSearch = True
    res = requests.post(url+'/getUserList', data=json.dumps(data), cookies=cookies)

    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        if res.json().get('total_row')[0].get('sum'):
          total_row= int(res.json().get('total_row')[0].get('sum'))
        else:
          total_row = 0
        users = []
        for pos,line in enumerate (data):
          linedata = {}
          linedata.update({"id":line.get('id'),"STT":pos+1,"UserName":line.get('Code'), "UserLocked":('' if line.get('UserLocked') == False else 'Locked'),'NameDisplay':line.get('NameDisplay'), 'LastSignOnDateTime':line.get('LastSignOnDateTime'), 'LastUpdateUserName':line.get('LastUpdateUserName'), 'LastUpdateDateTime':line.get('LastUpdateDateTime')})
          users.append(linedata)
        if users:
          total_pages = (round(total_row/page_size) + 1 if round(total_row/page_size) < (total_row/page_size) else round(total_row/page_size))
          pagination = {'page':page,'total_pages': total_pages}
          # print(pagination.__dict__)
          if isSearch:
            return {'users':users, 'pagination':pagination}          
          template = render_template('user.html', title='User', auth=True, users = users, pagination=pagination)
          template_bytes = template.encode('utf-8')
          base64_bytes = base64.b64encode(template_bytes)
          base64_template = base64_bytes.decode('utf-8')
          # return template
          return redirect(url_for('uaa_blueprint.SsoTs',template=base64_template))
        if isSearch:
          return {'users':None}
        template = render_template('user.html', title='User', auth=True)
        template_bytes = template.encode('utf-8')
        base64_bytes = base64.b64encode(template_bytes)
        base64_template = base64_bytes.decode('utf-8')
        return redirect(url_for('uaa_blueprint.SsoTs',template=base64_template))
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
@uaa.route('/user_detail',methods=['GET','POST'])
def user_detail():
    cookies = request.cookies
    url = Config.UAA_URL
    jwt_token = cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url): 
        return redirect('Accessisdenied')    
    data = request.values
    
    UserId = data.get('id')
    if request.method == 'POST':
      UserLocked =data.get('UserLocked','off')
      Password = data.get('Password')
      NameDisplay = data.get('NameDisplay',None)
      DataPermission = data.get('DataPermission',None)
      data = {}
      data.update({'id':UserId, 'TableName':'UserDefine'})
      if UserLocked:
        data.update({'UserLocked':UserLocked})
      if Password:
        data.update({'Password':Password})
      data.update({'NameDisplay':NameDisplay})
      data.update({'DataPermission':DataPermission})
      res = requests.post(url+'/updateUser', data=json.dumps(data), cookies=cookies)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')
      xrole =request.form.getlist('xrole')
      data2 ={'UserId':UserId, 'RoleList':xrole}
      res = requests.post(url+'/updateUserRole', data=json.dumps(data2), cookies=cookies)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')      
    '''user'''
    res = requests.post(url+'/getUserInfo', data=json.dumps({'id':UserId}), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        user = res.json().get('data')[0]
    elif res.status_code == 403:
      return redirect('Accessisdenied')
    else:
      return redirect('home')
    '''datapermission'''    
    datapermission = {'id':user.get('DataPermissionId'),'text':user.get('DataPermission')}
    '''roles'''
    res = requests.post(url+'/getRoleByUser', data=json.dumps({'id':UserId}), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        userrole = res.json().get('data')
        roles = []
        for rp in userrole:
          roles.append({'id':rp.get('RoleId'),'text':rp.get('Role')})    
    elif res.status_code == 403:
      return redirect('Accessisdenied')
    else:
      return redirect('home')
    return render_template('userdetail.html', title='User', auth=True, user = user, roles = roles, datapermission = datapermission)
"""
Roles
"""
@uaa.route('/Role',methods=['GET','POST'])
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
    res = requests.post(url+'/getRoleList', data=json.dumps(data), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        if res.json().get('total_row')[0].get('sum'):
          total_row= int(res.json().get('total_row')[0].get('sum'))
        else:
          total_row = 0
        roles = []
        for pos,line in enumerate (data):
          linedata = {}
          linedata.update({"id":line.get('id'),"STT":pos+1,"RoleName":line.get('Code'), 'Description':line.get('Description'), 'LastUpdateUserName':line.get('LastUpdateUserName'), 'LastUpdateDateTime':line.get('LastUpdateDateTime')})
          roles.append(linedata)
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
          return redirect(url_for('uaa_blueprint.SsoTs',template=base64_template))
        if isSearch:
          return {'users':None}
        template = render_template('role.html', title='Role', auth=True)
        template_bytes = template.encode('utf-8')
        base64_bytes = base64.b64encode(template_bytes)
        base64_template = base64_bytes.decode('utf-8')
        return redirect(url_for('uaa_blueprint.SsoTs',template=base64_template))
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
@uaa.route('/role_searching',methods=['GET','POST'])
def role_searching():
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    data = {}
    data.update(json.loads(request.data.decode('utf-8')))
    return redirect(url_for('role_blueprint.Role',data = json.dumps(data)))
@uaa.route('/getUserByRole',methods=['GET','POST'])
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
@uaa.route('/getRoleByPermission',methods=['GET','POST'])
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
@uaa.route('/role_deletion',methods=['GET','POST'])
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
@uaa.route('/role_detail',methods=['GET','POST'])
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
        res = requests.post(url+'/updateRole', data=json.dumps(data), cookies=cookies)
      else:        
        Code = data.get('RoleName',None)
        data.update({'Code':Code})
        res = requests.post(url+'/addRole', data=json.dumps(data), cookies=cookies)
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
      res = requests.post(url+'/getRoleInfo', data=json.dumps({'id':RoleId}), cookies=cookies)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          role = res.json().get('data')[0]
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
      '''rolepermission'''
      res = requests.post(url+'/getPermissionByRole', data=json.dumps({'id':RoleId}), cookies=cookies)
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
Permissions
"""
@uaa.route('/Permission',methods=['GET'])
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
    res = requests.post(url+'/getPermissionList', data=json.dumps(data), cookies=cookies)  
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        if res.json().get('total_row')[0].get('sum'):
          total_row= int(res.json().get('total_row')[0].get('sum'))
        else:
          total_row = 0
        permissions = []
        for pos,line in enumerate (data):
          linedata = {}
          linedata.update({"id":line.get('id'),"STT":pos+1,"PermissionName":line.get('Code'),"PermissionType":line.get('PermissionType'), 'Description':line.get('Description'), 'LastUpdateUserName':line.get('LastUpdateUserName'), 'LastUpdateDateTime':line.get('LastUpdateDateTime')})
          permissions.append(linedata)
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
@uaa.route('/permission_detail',methods=['GET','POST'])
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
      UrlTable_base64 = data.get('UrlTable_base64')
      UrlList = []
      if UrlTable_base64:
        base64_bytes = UrlTable_base64.encode('utf-8')
        UrlTable_bytes = base64.b64decode(base64_bytes)
        UrlTable = UrlTable_bytes.decode('utf-8')
        UrlList.append(UrlTable)
      data = {}
      data.update({'Description':Description,'PermissionType':PermissionType,'UrlList':UrlList})
      if PermissionId != "New":
        data.update({'PermissionId':PermissionId})
        res = requests.post(url+'/updatePermission', data=json.dumps(data), cookies=cookies)
      else:        
        Code = data.get('PermissionName',None)
        data.update({'Code':Code})
        res = requests.post(url+'/addPermission', data=json.dumps(data), cookies=cookies)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')
         
    if PermissionId !='New':
      '''permission'''
      res = requests.post(url+'/getPermissionInfo', data=json.dumps({'ids':[PermissionId]}), cookies=cookies)
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
      res = requests.post(url+'/getURLbyPermission', data=json.dumps(data), cookies=cookies)
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
@uaa.route('/getURLbyPermission',methods=['GET', 'POST'])
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
    res = requests.post(url+'/getURLbyPermission', data=json.dumps(data), cookies=cookies)
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
@uaa.route('/permission_searching',methods=['GET','POST'])
def permission_searching():
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if not xauth:# or not check_url(session['URLList'],request.base_url,Method = request.method, Type = 'page'):
      return redirect('Accessisdenied')
    data = {}
    data.update(json.loads(request.data.decode('utf-8')))
    return redirect(url_for('permission_blueprint.Permission',data = json.dumps(data)))
@uaa.route('/permission_deletion',methods=['GET','POST'])
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
    res = requests.post(url+'/deletePermissionById', data=json.dumps(data), cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
    return redirect(url_for('permission_blueprint.Permission'))
"""
select2
"""
@uaa.route('/getRoleList',methods=['POST'])
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
@uaa.route('/getDataPermissionList',methods=['POST'])
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
  res = requests.post(url+'/getDataPermissionList', data=json.dumps(data), cookies=cookies)
  if res.status_code == 200:
    if res.json().get('status','') == 'OK':
      data= res.json().get('data')
      datapermissions = []
      for d in data:
        datapermissions.append({"id":d.get("id"),"text":d.get("Code")})
      datapermissions = list({v['id']:v for v in datapermissions}.values())
      return json.dumps(datapermissions)
@uaa.route('/getRolePermissionList',methods=['POST'])
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
  res = requests.post(url+'/getRolePermissionList', data=json.dumps(data), cookies=cookies)
  if res.status_code == 200:
    if res.json().get('status','') == 'OK':
      data= res.json().get('data') 
      permissions = []
      for d in data:
        permissions.append({"id":d.get("id"),"text":d.get("Code")})
      permissions = list({v['id']:v for v in permissions}.values())
      return json.dumps(permissions)
