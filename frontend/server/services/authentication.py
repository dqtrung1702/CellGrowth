from flask import Blueprint, request,redirect,url_for,render_template,session
import requests
from config import Config
from base import auth
authentication = Blueprint('auth_blueprint',__name__)

@authentication.route('/login',methods=['GET', 'POST'])
def login():
    print('*********************login*********************')
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if xauth:
      return redirect(url_for('home_blueprint.home'))
    else:
      if request.method == 'POST':
        session.clear()  # reset menu/data scopes from previous user
        data = request.form
        url = Config.UAA_URL

        # Branch 1: submit OTP after receiving mfa_token
        if data.get('mfa_token') and data.get('otp'):
          payload = {'Code': data.get('otp'), 'mfa_token': data.get('mfa_token')}
          try:
            res = requests.post(url + '/mfa/totp/verify_login', json=payload, timeout=5)
            res_body = res.json() if res.content else {}
          except Exception as exc:
            return render_template('login_totp.html', title='Error', error=f'OTP verify failed: {exc}', auth=False, mfa_token=data.get('mfa_token'))
          if res.status_code == 200 and res_body.get('status') == 'OK':
            jwt_token = res_body.get('token') or (res_body.get('data') or {}).get('token','')
            resp = redirect(url_for('home_blueprint.home'))
            resp.set_cookie('app_token', jwt_token, path='/', httponly=True, samesite="Lax")
            return resp
          error_detail = res_body or res.text or f'Unexpected status code {res.status_code}'
          return render_template('login_totp.html', title='Error', error=error_detail, auth=False, mfa_token=data.get('mfa_token'))

        # Branch 2: username/password
        payload={'UserName': data.get('username'),'Password': data.get('password')}
        resp = redirect(url_for('home_blueprint.home'))
        try:
          res = requests.post(url + '/login', json=payload, timeout=5)
        except requests.RequestException as exc:
          return render_template('login.html', title='Error', error=f'Authentication service unreachable: {exc}', auth=False)

        try:
          res_body = res.json() if res.content else {}
        except ValueError:
          res_body = {}

        if res.status_code == 200:
          status = res_body.get('status','')
          if status == 'OK':
            jwt_token = res_body.get('token','')
            if not isinstance(jwt_token, str) or not jwt_token:
              error_detail = res_body or res.text or 'Login OK but token missing'
              return render_template('login.html', title='Error', error=error_detail, auth=False)
            resp.set_cookie('app_token', jwt_token, path='/', httponly=True, samesite="Lax")
            return resp
          if status == 'OTP_REQUIRED':
            mfa_token = res_body.get('mfa_token','')
            return render_template('login_totp.html', title='Login - OTP', auth=False, mfa_token=mfa_token)

        # Build a user-friendly error when the upstream response is not JSON or status is unexpected.
        error_detail = res_body or res.text or f'Unexpected status code {res.status_code}'
        return render_template('login.html', title='Error', error=error_detail, auth=False)
      else:
        return render_template('login.html', title='Login', auth=False)

@authentication.route('/logout')
def logout():
  resp = redirect(url_for('home_blueprint.home'))
  resp.delete_cookie('app_token')
  session.clear()
  return resp

@authentication.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      session.clear()  # clear any old menu/data from previous session
      data = request.form
      url = Config.UAA_URL + '/register'
      role_codes = [c.strip() for c in (data.getlist('role_codes') or []) if c.strip()]
      dp_codes = [c.strip() for c in (data.getlist('data_permission_codes') or []) if c.strip()]
      payload={
        'Code': data.get('username'),
        'Password': data.get('password'),
        'NameDisplay': data.get('namedisplay'),
        'RoleCodes': role_codes,
        'DataPermissionCodes': dp_codes,
        'Reason': data.get('reason'),
        'TtlHours': data.get('ttl_hours')
      }
      # Gửi JSON chuẩn để UAA nhận được body
      res = requests.post(url, json=payload, timeout=5)
      if res.status_code == 200:
        if res.json().get('status','') == 'OK':
          jwt_token = res.json().get('token','')
          resp = redirect(url_for('home_blueprint.home'))
          resp.set_cookie('app_token', jwt_token, path='/', httponly=True, samesite="Lax")
          return resp
        else:
          return render_template('register.html', title='Error', error=res.text, auth=False)
      else:
        return render_template('register.html', title='Error', error=res.text, auth=False)
    else:
      # preload options for select boxes
      roles = []
      data_perms = []
      try:
        rres = requests.get(Config.UAA_URL + '/publicRoleList', timeout=5)
        roles = (rres.json() or {}).get('data', []) if rres.status_code == 200 else []
      except Exception:
        roles = []
      try:
        dres = requests.get(Config.UAA_URL + '/publicPermissionList', timeout=5)
        data_perms = (dres.json() or {}).get('data', []) if dres.status_code == 200 else []
      except Exception:
        data_perms = []
      return render_template('register.html', title='Register', auth=False, roles=roles, data_perms=data_perms)
