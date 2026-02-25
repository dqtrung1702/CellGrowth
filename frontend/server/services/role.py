from datetime import datetime
from flask import Blueprint, request,redirect,url_for,render_template
import requests
from config import Config
import json
from base import require_page_access
import base64
import sys
import re

def _fmt_dt(val):
    """Convert datetime/pg/bson style to string for UI."""
    if isinstance(val, dict) and '$date' in val:
        v = val.get('$date')
        return v if isinstance(v, str) else str(v)
    if hasattr(val, 'isoformat'):
        try:
            return val.isoformat()
        except Exception:
            pass
    return '' if val is None else str(val)

def _date_key(val):
    """Normalize date/datetime to ISO date string (YYYY-MM-DD) for filtering."""
    s = _fmt_dt(val)
    if not s:
        return None
    if not isinstance(s, str):
        s = str(s)
    try:
        return datetime.fromisoformat(s.replace('Z','+00:00')).date().isoformat()
    except Exception:
        pass
    parts = [p for p in re.split(r'\D+', s) if p]
    if len(parts) >= 3:
        try:
            if len(parts[0]) == 4:  # Y M D
                y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            else:  # assume D M Y
                d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                if len(parts[2]) == 2:
                    y += 2000 if y < 70 else 1900
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            pass
    return s

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
@require_page_access
def Role():
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
    if res.status_code != 200:
      return redirect('home')
    if res.json().get('status','') != 'OK':
      if res.status_code == 403:
        return redirect('Accessisdenied')
      return redirect('home')

    data_rows = res.json().get('data') or []
    total_raw = res.json().get('total_row') or []
    total_row = int(total_raw[0].get('sum')) if total_raw and total_raw[0].get('sum') else 0
    roles = []
    for pos,line in enumerate (data_rows):
      roles.append({
        "id": line.get('id'),
        "STT": pos+1,
        "RoleName": line.get('Code'),
        "Description": line.get('Description'),
        "LastUpdateDateTime": _fmt_dt(line.get('LastUpdateDateTime'))
      })
    total_pages = (round(total_row/page_size) + 1 if round(total_row/page_size) < (total_row/page_size) else round(total_row/page_size)) if page_size else 1
    pagination = {'page':page,'total_pages': total_pages}
    if isSearch:
      return {'roles':roles, 'pagination':pagination}
    template = render_template('role.html', title='Role', auth=True, roles = roles, pagination=pagination)
    return template
@role.route('/role_searching',methods=['GET','POST'])
@require_page_access
def role_searching():
    # Return JSON result directly instead of redirect to keep AJAX simple
    cookies = request.cookies
    url = Config.UAA_URL
    ui_page_size = Config.PAGE_SIZE
    payload = {}
    try:
      payload.update(json.loads(request.data.decode('utf-8')))
    except Exception:
      pass
    page = int(payload.get('page', 1) or 1)
    code_filter = payload.get('Code')
    desc_filter = (payload.get('Description') or '').lower()
    date_filter = (payload.get('LastUpdateDateTime') or '').strip()
    date_filter_key = _date_key(date_filter) if date_filter else None
    print("[role_searching] input", json.dumps(payload), "date_key", date_filter_key, file=sys.stderr)

    # fetch a larger page from UAA, then filter locally on Description/LastUpdateDateTime
    fetch_payload = {
      'page': 1,
      'page_size': max(500, ui_page_size),
      'Code': code_filter
    }
    res = requests.post(url+'/getRoleList', json=fetch_payload, cookies=cookies, timeout=5)
    if res.status_code == 200 and res.json().get('status') == 'OK':
      data = res.json().get('data', [])
      filtered = []
      for line in data:
        desc = (line.get('Description') or '').lower()
        last = (line.get('LastUpdateDateTime') or '')
        last_key = _date_key(last)
        if desc_filter and desc_filter not in desc:
          continue
        if date_filter_key and date_filter_key != last_key:
          continue
        if date_filter and not date_filter_key and date_filter not in last:
          continue
        filtered.append(line)
      total_row = len(filtered)
      print("[role_searching] fetched", len(data), "filtered", total_row, file=sys.stderr)
      # paginate manually for UI
      start = (page-1)*ui_page_size
      end = start + ui_page_size
      page_items = filtered[start:end]
      roles = []
      for pos,line in enumerate (page_items, start=1+start):
        roles.append({
          "id": line.get('id'),
          "STT": pos,
          "RoleName": line.get('Code'),
          "Description": line.get('Description'),
          "LastUpdateDateTime": _fmt_dt(line.get('LastUpdateDateTime'))
        })
      total_pages = int((total_row + ui_page_size - 1) / ui_page_size) or 1
      pagination = {'page':page,'total_pages': total_pages}
      return {'roles':roles, 'pagination':pagination}
    return {'roles':[], 'pagination':{'page':1,'total_pages':1}, 'status':'FAIL'}, res.status_code
@role.route('/getUserByRole',methods=['GET','POST'])
@require_page_access
def getUserByRole():
    cookies = request.cookies
    url = Config.UAA_URL
    data = json.loads(request.data.decode('utf-8'))
    RoleId = data.get('id')
    data = {'id':RoleId}
    # UAA expects JSON body; use json= to set header + serialization
    res = requests.post(url+'/getUserByRole', json=data, cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        userlist = []
        for d in data:
          userlist.append(d.get('UserName'))
        if userlist:
          return 'List of users who will lose this role:\n-' + '\n-'.join(userlist) + '\nAre you sure?'
        return 'Are you sure?'
    # fallback for error cases
    try:
      msg = res.json().get('message','Request failed')
    except Exception:
      msg = 'Request failed'
    return msg, res.status_code
@role.route('/getRoleByPermission',methods=['GET','POST'])
@require_page_access
def getRoleByPermission():
    cookies = request.cookies
    url = Config.UAA_URL
    data = json.loads(request.data.decode('utf-8'))
    PermissionId = data.get('id')
    data = {'id':PermissionId}
    # UAA expects JSON body; use json= to set header + serialization
    res = requests.post(url+'/getRoleByPermission', json=data, cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
        rolelist = []
        for d in data:
          rolelist.append(d.get('RoleName'))
        if rolelist:
          return 'List of roles which will lose this permission:\n-' + '\n-'.join(rolelist) + '\nAre you sure?'
        return 'Are you sure?'
    # fallback for error cases
    try:
      msg = res.json().get('message','Request failed')
    except Exception:
      msg = 'Request failed'
    return msg, res.status_code
@role.route('/role_deletion',methods=['GET','POST'])
@require_page_access
def role_deletion():
    cookies = request.cookies
    url = Config.UAA_URL
    data = request.values
    RoleId = data.get('id')
    data = {'id':RoleId}
    res = requests.post(url+'/deleteRoleById', json=data, cookies=cookies)
    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        data= res.json().get('data')
    return redirect(url_for('role_blueprint.Role'))
@role.route('/role_detail',methods=['GET','POST'])
@require_page_access
def role_detail():
    cookies = request.cookies
    url = Config.UAA_URL
    incoming = request.values
    RoleId = incoming.get('id')
    if request.method == 'POST':
      Description = incoming.get('Description',None)
      Permission = incoming.getlist('Permission',None)
      RoleName = incoming.get('RoleName', None)
      data = {}
      data.update({'Description':Description,'Permission':Permission})
      if RoleId != "New":
        data.update({'RoleId':RoleId})
        res = requests.post(url+'/updateRole', json=data, cookies=cookies, timeout=5)
      else:        
        # UAA requires the role code when creating a new role
        data.update({'Code':RoleName})
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
          # normalize field so template can show RoleName
          role['RoleName'] = role.get('Code')
          role['LastUpdateDateTime'] = _fmt_dt(role.get('LastUpdateDateTime'))
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
@require_page_access
def getRoleList():
  cookies = request.cookies
  url = Config.UAA_URL
  data = json.loads(request.data.decode('utf-8'))
  page = data.get('page',1)
  Code = data.get('Code')
  data = {'Code':Code,'page' : page,'page_size' : Config.PAGE_SIZE}
  res = requests.post(url+'/getRoleList', json=data, cookies=cookies)
  if res.status_code == 200:
    if res.json().get('status','') == 'OK':
      data= res.json().get('data') 
      roles = []
      for d in data:
        roles.append({"id":d.get("id"),"text":d.get("Code")})      
      roles = list({v['id']:v for v in roles}.values())
      return json.dumps(roles)
