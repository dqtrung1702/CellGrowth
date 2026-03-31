from flask import Blueprint, render_template, request, redirect, session
from base import auth_info
from config import Config
import requests

home_ = Blueprint(
    'home_blueprint'
    ,__name__
    # ,static_folder="../../client/static/home"
    # ,template_folder= "../../client/template/home"
)


PAGE_MENU_MAP = {
    "home": "Home",
    "role": "Roles",
    "permission": "Permissions",
    "user": "Users",
    "datasets": "DataSets",
    "access_requests": "AccessRequests",
    "mfa/totp/setup": "TOTP",
}


def _build_menu_flags(page_items):
    # Home luôn hiển thị; AccessRequests hiển thị mặc định để user có thể gửi/xem yêu cầu của chính mình
    flags = {"Home": True, "AccessRequests": True}
    for item in page_items or []:
        page = (item or {}).get("Page") or (item or {}).get("page") or ""
        norm = page.strip().strip("/").lower()
        menu_id = PAGE_MENU_MAP.get(norm)
        if menu_id:
            flags[menu_id] = True
    return flags


@home_.route('/')
@home_.route('/home')
def home():
    cookies = request.cookies
    jwt_token = cookies.get('app_token','')  
    xauth,xinfo = auth_info(jwt_token)
    if not xauth:        
        return redirect('login')
    # Always refresh page permissions -> MenuFlags to reflect recent changes
    url = Config.UAA_URL
    payload = {'UserId': xinfo.get('UserId')}
    try:
        res = requests.post(url+'/getPageByUser', json=payload, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status') == 'OK':
            pages = res.json().get('data', [])
            session['MenuFlags'] = _build_menu_flags(pages)
        else:
            session['MenuFlags'] = _build_menu_flags([])
    except Exception:
        session['MenuFlags'] = _build_menu_flags([])

    # Refresh DataScopes as well (kept consistent with page refresh)
    try:
        res = requests.post(url+'/getDataSetByUser', json=payload, cookies=cookies, timeout=5)
        if res.status_code == 200 and res.json().get('status') == 'OK':
            session['DataScopes'] = res.json().get('data', [])
    except Exception:
        session['DataScopes'] = []
    return render_template('home.html', title='Home', auth=True, uaa_url=Config.UAA_URL)


@home_.route('/Accessisdenied')
def Accessisdenied():
    return render_template('Accessisdenied.html', title='Access is denied', auth=False), 403
