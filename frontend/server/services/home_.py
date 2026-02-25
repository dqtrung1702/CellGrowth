from flask import Blueprint, render_template, request, redirect, session
from base import auth_info
from config import Config
import requests
import json

home_ = Blueprint(
    'home_blueprint'
    ,__name__
    # ,static_folder="../../client/static/home"
    # ,template_folder= "../../client/template/home"
)


@home_.route('/')
@home_.route('/home')
def home():
    cookies = request.cookies
    jwt_token = cookies.get('app_token','')  
    xauth,xinfo = auth_info(jwt_token)
    if not xauth:        
        return redirect('login')
    if 'URLList' not in session:
        url = Config.UAA_URL
        data = json.dumps({'PermissionList' : xinfo.get('Permissions')})
        res = requests.post(url+'/getURLbyPermissionList', data=data, cookies=cookies)
        if res.status_code == 200:
            if res.json().get('status','') == 'OK':                
                URLList = res.json().get('data')
                session['URLList'] = URLList
    if 'DataScopes' not in session:
        url = Config.UAA_URL
        payload = {'UserId': xinfo.get('UserId')}
        try:
            res = requests.post(url+'/getDataSetByUser', json=payload, cookies=cookies, timeout=5)
            if res.status_code == 200 and res.json().get('status') == 'OK':
                session['DataScopes'] = res.json().get('data', [])
        except Exception:
            pass
    return render_template('home.html', title='Home', auth=True)


@home_.route('/Accessisdenied')
def Accessisdenied():
    return render_template('Accessisdenied.html', title='Access is denied', auth=False), 403
