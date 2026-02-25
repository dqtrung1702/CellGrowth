from datetime import datetime
from flask import Blueprint, request,redirect,render_template
import requests
from config import Config
import jwt
import json
from base import require_page_access
import re
import math
import base64

def _fmt_dt(val):
    """Convert datetime/dict/$date to string for UI display."""
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

def _auth_user_id(jwt_token):
    try:
        data = jwt.decode(jwt_token, Config.JWT_SECRET, algorithms=Config.JWT_ALGORITHM)
        return data.get('UserId')
    except Exception:
        return None


def _fetch_scopes_for_user(user_id, cookies):
    """Fetch data scopes strictly by user's DataPermissionId (role cannot grant DATA)."""
    if not user_id:
        return []
    try:
        res_info = requests.post(Config.UAA_URL + '/getUserInfo', json={'id': user_id}, cookies=cookies, timeout=5)
        if res_info.status_code == 200 and res_info.json().get('status') == 'OK':
            data_perm_id = (res_info.json().get('data') or [{}])[0].get('DataPermissionId')
            if data_perm_id:
                res_dp = requests.post(Config.UAA_URL + '/getDatasetByPermission',
                                       json={'PermissionId': data_perm_id},
                                       cookies=cookies,
                                       timeout=5)
                if res_dp.status_code == 200 and res_dp.json().get('status') == 'OK':
                    return res_dp.json().get('data', [])
    except Exception:
        pass
    return []


def _make_scope_filter(scopes, service='uaa', table='users'):
    """Return a predicate(row) respecting scopes. Wildcard -> allow all."""
    if not scopes:
        # No data permission -> deny all rows
        return lambda row: False
    service = (service or '').lower()
    table = (table or '').lower()

    filters = []
    has_wildcard = False
    for sc in scopes:
        svc = (sc.get('Services') or '*').lower()
        tbl = (sc.get('Table') or '*').lower()
        col = sc.get('Column') or '*'
        val = sc.get('Value') or '*'
        if svc not in ('*', service):
            continue
        if tbl not in ('*', table):
            continue
        if col == '*' or val == '*':
            has_wildcard = True
            continue
        filters.append((col, str(val)))

    if has_wildcard and not filters:
        return None  # allow all
    if not filters:
        return lambda row: False  # deny all if no usable scope

    def predicate(row):
        # normalize keys to lowercase for case-insensitive matching
        row_l = {str(k).lower(): v for k, v in row.items()}
        for col, val in filters:
            if str(row_l.get(col)) == val:
                return True
        return False

    return predicate

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
@require_page_access
def User():
    cookies = request.cookies
    url = Config.UAA_URL
    payload = {}
    page_size = Config.PAGE_SIZE
    page =  request.args.get('page', type=int, default=1)
    payload.update({'page' : page,'page_size' : page_size})
    isSearch = False
    if request.data:
      try:
        payload.update(json.loads(request.data.decode('utf-8')))
      except Exception:
        pass
      page = payload.get('page', page)
      isSearch = True
    res = requests.post(url+'/getUserList', json=payload, cookies=cookies, timeout=5)

    if res.status_code == 200:
      if res.json().get('status','') == 'OK':
        rows = res.json().get('data') or []
        # build data-scope filter for current user
        jwt_token = cookies.get('app_token','')
        uid = _auth_user_id(jwt_token)
        scopes = _fetch_scopes_for_user(uid, cookies)
        scope_filter = _make_scope_filter(scopes, service='uaa', table='users')

        # recompute total rows after scope filter
        total_row = 0
        # filters
        user_filter = (payload.get('UserName') or '').lower()
        last_sign_filter = (payload.get('LastSignOnDateTime') or '').strip()
        last_sign_filter_key = _date_key(last_sign_filter) if last_sign_filter else None
        last_update_filter = (payload.get('LastUpdateDateTime') or '').strip()
        last_update_filter_key = _date_key(last_update_filter) if last_update_filter else None
        users = []
        for line in rows:
          # apply date filters locally (trunc to date)
          last_sign = line.get('LastSignOnDateTime')
          last_upd = line.get('LastUpdateDateTime')
          if user_filter and user_filter not in (line.get('UserName','').lower()):
            continue
          if last_sign_filter_key and last_sign_filter_key != _date_key(last_sign):
            continue
          if last_sign_filter and not last_sign_filter_key and last_sign_filter not in _fmt_dt(last_sign):
            continue
          if last_update_filter_key and last_update_filter_key != _date_key(last_upd):
            continue
          if last_update_filter and not last_update_filter_key and last_update_filter not in _fmt_dt(last_upd):
            continue
          if scope_filter and not scope_filter(line):
            continue
          total_row += 1
          users.append({
            "id": line.get('id'),
            "STT": total_row,
            "UserName": line.get('UserName'),
            "LastSignOnDateTime": _fmt_dt(line.get('LastSignOnDateTime')),
            "LastUpdateDateTime": _fmt_dt(line.get('LastUpdateDateTime'))
          })
        total_pages = int(math.ceil(total_row / page_size)) if page_size else 1
        pagination = {'page':page,'total_pages': total_pages}
        if isSearch:
          return {'users':users, 'pagination':pagination}
        template = render_template('user.html', title='User', auth=True, users = users, pagination=pagination)
        return template
      elif isSearch:
        return {'users':[], 'pagination':{'page':1,'total_pages':1}}
      # fallback: no data but non-ajax request -> render empty page with pagination default
      template = render_template('user.html', title='User', auth=True, users=[], pagination={'page':1,'total_pages':1})
      return template
    elif res.status_code == 403:
      return redirect('Accessisdenied')
    else:
      return redirect('home')
@user.route('/user_detail',methods=['GET','POST'])
@require_page_access
def user_detail():
    cookies = request.cookies
    url = Config.UAA_URL
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
        user['LastSignOnDateTime'] = _fmt_dt(user.get('LastSignOnDateTime'))
        user['LastUpdateDateTime'] = _fmt_dt(user.get('LastUpdateDateTime'))
        # scope check: current viewer must have data permission to see this user
        jwt_token = cookies.get('app_token','')
        viewer_id = _auth_user_id(jwt_token)
        scopes = _fetch_scopes_for_user(viewer_id, cookies)
        scope_filter = _make_scope_filter(scopes, service='uaa', table='users')
        if scope_filter and not scope_filter(user):
          return redirect('Accessisdenied')
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
