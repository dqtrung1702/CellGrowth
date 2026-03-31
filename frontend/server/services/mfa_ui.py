from flask import Blueprint, request, render_template, redirect, url_for
import requests
from base import require_page_access, issue_csrf_token
from config import Config

mfa_ui = Blueprint('mfa_ui', __name__)


def _csrf():
    """Ensure a CSRF token exists in session and return it for forms."""
    return issue_csrf_token()


@mfa_ui.route('/mfa/totp/setup', methods=['GET', 'POST'])
@require_page_access
def totp_setup():
    cookies = request.cookies
    url = Config.UAA_URL
    error = None
    success = None
    secret = None
    provisioning_uri = None

    # Disable request
    if request.method == 'POST' and request.form.get('action') == 'disable':
        try:
            res = requests.post(url + '/mfa/totp/disable', json={}, cookies=cookies, timeout=5)
            if res.status_code == 200 and (res.json() or {}).get('status') == 'OK':
                success = 'Đã tắt xác thực OTP cho tài khoản.'
            else:
                error = res.text or 'Không tắt được OTP.'
        except Exception as exc:
            error = f'Lỗi kết nối: {exc}'
        return render_template('totp_setup.html', title='TOTP', auth=True, secret=None, provisioning_uri=None,
                               error=error, success=success, csrf_token=_csrf())

    # Verify code request
    if request.method == 'POST':
        code = request.form.get('otp')
        try:
            res = requests.post(url + '/mfa/totp/verify', json={'Code': code}, cookies=cookies, timeout=5)
            if res.status_code == 200 and (res.json() or {}).get('status') == 'OK':
                success = 'Kích hoạt OTP thành công. Từ lần đăng nhập tiếp theo bạn sẽ cần mã 6 số.'
            else:
                error = (res.json() or {}).get('message') if res.content else res.text
        except Exception as exc:
            error = f'Lỗi kết nối: {exc}'
        return render_template('totp_setup.html', title='TOTP', auth=True, secret=None, provisioning_uri=None,
                               error=error, success=success, csrf_token=_csrf())

    # GET: enroll to fetch secret/URI
    try:
        res = requests.post(url + '/mfa/totp/enroll', json={}, cookies=cookies, timeout=5)
        body = res.json() if res.content else {}
        if res.status_code == 200 and body.get('status') == 'OK':
            data = body.get('data') or {}
            if data.get('already_enabled'):
                success = 'OTP đã được kích hoạt trước đó.'
            else:
                secret = data.get('secret')
                provisioning_uri = data.get('provisioning_uri')
        else:
            error = body or res.text or 'Không lấy được mã OTP.'
    except Exception as exc:
        error = f'Lỗi kết nối: {exc}'

    return render_template('totp_setup.html', title='TOTP', auth=True, secret=secret, provisioning_uri=provisioning_uri,
                           error=error, success=success, csrf_token=_csrf())


__all__ = ['mfa_ui']
