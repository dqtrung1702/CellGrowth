from datetime import datetime
from flask import Blueprint, request,redirect,url_for,render_template,session,make_response
import requests
from config import Config
import jwt
import json
from base import check_url,auth
import base64
user = Blueprint(
    'user_blueprint',
    __name__,
  )
"""
Utility
"""
@user.route('/SsoTs',methods=['GET','POST'])
def SsoTs():
    base64_template = request.values.get('template')
    base64_bytes = base64_template.encode('utf-8')
    template_bytes = base64.b64decode(base64_bytes)
    template = template_bytes.decode('utf-8')
    return template
"""
Users
"""
@user.route('/User',methods=['GET','POST'])
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
    res = requests.post(url+'/getUserList', json=data, cookies=cookies, timeout=5)

    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        if res.json().get('total_row')[0].get('sum'):
          total_row= int(res.json().get('total_row')[0].get('sum'))
        else:
          total_row = 0
        users = []
        for pos,line in enumerate (data):
          users.append({
            "id": line.get('id'),
            "STT": pos+1,
            "UserName": line.get('UserName'),
            "LastSignOnDateTime": line.get('LastSignOnDateTime'),
            "LastUpdateDateTime": line.get('LastUpdateDateTime')
          })
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
          return template
          # return redirect(url_for('user_blueprint.SsoTs',template=base64_template))
        if isSearch:
          return {'users':None}
        template = render_template('user.html', title='User', auth=True)
        template_bytes = template.encode('utf-8')
        base64_bytes = base64.b64encode(template_bytes)
        base64_template = base64_bytes.decode('utf-8')
        # return redirect(url_for('user_blueprint.SsoTs',template=base64_template))
        return template
      elif res.status_code == 403:
        return redirect('Accessisdenied')
      else:
        return redirect('home')
@user.route('/user_detail',methods=['GET','POST'])
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
      res = requests.post(url+'/updateUser', json=data, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')
      xrole =request.form.getlist('xrole')
      data2 ={'UserId':UserId, 'RoleList':xrole}
      res = requests.post(url+'/updateUserRole', json=data2, cookies=cookies, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          data= res.json().get('data')
        elif res.status_code == 403:
          return redirect('Accessisdenied')
        else:
          return redirect('home')      
    '''user'''
    res = requests.post(url+'/getUserInfo', json={'id':UserId}, cookies=cookies, timeout=5)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        user = res.json().get('data')[0]
    elif res.status_code == 403:
      return redirect('Accessisdenied')
    else:
      return redirect('home')
    '''datapermission'''    
    dp_id = user.get('DataPermissionId')
    dp_text = user.get('DataPermission') or ''
    datapermission = {'id': dp_id, 'text': dp_text} if dp_id else {}
    '''roles'''
    res = requests.post(url+'/getRoleByUser', json={'id':UserId}, cookies=cookies, timeout=5)
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
