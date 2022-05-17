from datetime import datetime
from flask import Blueprint, request,redirect,url_for,render_template,session,make_response
import requests
from config import Config
import jwt
import json
from base import check_url,auth
import base64
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
        res = requests.post(url  + '/login', headers = {}, data=json.dumps(payload))
        if res.status_code == 200:
          if res.json().get('status','') == 'OK':
            jwt_token = res.json().get('token','')            
          else:
            return render_template('login.html', title='Error', error=res.json(), auth=False)
        else:
          return render_template('login.html', title='Error', error=res.json(), auth=False)
        resp.set_cookie('app_token', res.json().get('token'))
        return resp
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
