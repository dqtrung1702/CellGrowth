from flask import Blueprint, request,redirect,url_for,render_template,session
import requests
from config import Config
from base import auth
authentication = Blueprint('auth_blueprint',__name__)

@authentication.route('/login',methods=['GET', 'POST'])
def login():
    print('*********************login*********************')
    if 'URLList' in session:
      session.pop('URLList',None)
    jwt_token = request.cookies.get('app_token','')  
    xauth = auth(jwt_token)
    if xauth:
      return redirect(url_for('home_blueprint.home'))
    else:
      if request.method == 'POST':
        data = request.form
        url = Config.UAA_URL
        payload={'UserName': data.get('username'),'Password': data.get('password')}
        resp = redirect(url_for('home_blueprint.home'))
        print(payload)
        try:
          # Send JSON with proper headers; requests sets Content-Type automatically when using json=.
          res = requests.post(url + '/login', json=payload, timeout=5)
        except requests.RequestException as exc:
          return render_template('login.html', title='Error', error=f'Authentication service unreachable: {exc}', auth=False)

        try:
          res_body = res.json() if res.content else {}
        except ValueError:
          res_body = {}

        if res.status_code == 200 and res_body.get('status','') == 'OK':
          jwt_token = res_body.get('token','')
          resp.set_cookie('app_token', jwt_token, path='/', httponly=True, samesite="Lax")
          return resp

        # Build a user-friendly error when the upstream response is not JSON or status is unexpected.
        error_detail = res_body or res.text or f'Unexpected status code {res.status_code}'
        return render_template('login.html', title='Error', error=error_detail, auth=False)
      else:
        return render_template('login.html', title='Login', auth=False)

@authentication.route('/logout')
def logout():
  resp = redirect(url_for('home_blueprint.home'))
  resp.delete_cookie('app_token')
  return resp

@authentication.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      data = request.form
      url = Config.UAA_URL + '/register'
      payload={'Code': data.get('username'),'Password': data.get('password'), 'NameDisplay': data.get('namedisplay')}
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
      return render_template('register.html', title='Register', auth=False)
