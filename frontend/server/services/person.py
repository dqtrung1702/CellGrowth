from datetime import datetime
from flask import Blueprint, request, render_template, redirect
import requests
import json
from base import require_page_access
from config import Config


person = Blueprint(
    'person_blueprint',
    __name__,
)


def _call_person_api(path: str, payload: dict, cookies):
    url = Config.PERSON_URL.rstrip("/") + path
    try:
        res = requests.post(url, json=payload, cookies=cookies, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"status": "FAIL", "message": "Person service unavailable"}


def _fmt_date(val):
    """Format date/datetime to DD/MM/YYYY for UI."""
    if not val:
        return ""
    try:
        if isinstance(val, dict) and "$date" in val:
            iso = val["$date"]
        else:
            iso = val
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(val)


@person.route('/person', methods=['GET'])
@require_page_access
def person_list():
    cookies = request.cookies
    page = request.args.get('page', default=1, type=int)
    code = request.args.get('Code', '', type=str)
    full_name = request.args.get('FullName', '', type=str)
    page_size = Config.PAGE_SIZE

    payload = {
        "page": page,
        "page_size": page_size,
        "Code": code or None,
        "FullName": full_name or None,
    }
    # Clean None entries for nicer payload
    payload = {k: v for k, v in payload.items() if v not in (None, "")}

    res_json = _call_person_api('/searchPerson', payload, cookies)
    rows = res_json.get('data') or []
    total = res_json.get('total_row', len(rows))

    persons = []
    for idx, p in enumerate(rows, start=1 + (page - 1) * page_size):
        persons.append({
            "STT": idx,
            "id": p.get('_id') or p.get('id'),
            "Code": p.get('Code', ''),
            "FullName": p.get('FullName', ''),
            "BirthDate": _fmt_date(p.get('BirthDate')),
            "LastUpdateDateTime": _fmt_date(p.get('LastUpdateDateTime')),
            "LastUpdateUserName": p.get('LastUpdateUserName', ''),
        })

    total_pages = (total + page_size - 1) // page_size if page_size else 1
    pagination = {"page": page, "total_pages": total_pages}

    return render_template(
        'person.html',
        title='Person',
        auth=True,
        persons=persons,
        pagination=pagination,
        filters={"Code": code, "FullName": full_name},
        error=None if res_json.get('status') == 'OK' else res_json.get('message', 'Person service error'),
    )


@person.route('/person/detail', methods=['GET', 'POST'])
@require_page_access
def person_detail():
    cookies = request.cookies
    person_id = request.args.get('id') or request.form.get('id')

    if request.method == 'POST':
        code = request.form.get('Code', '').strip()
        full_name = request.form.get('FullName', '').strip()
        birth_date = request.form.get('BirthDate', '').strip()
        birth_place = request.form.get('BirthPlace', '').strip()
        nationality = request.form.get('Nationallity', '').strip()
        ethnic = request.form.get('Ethenic', '').strip()
        family_type = request.form.get('FamilyType', '').strip()

        payload = {
            "Code": code,
            "FullName": full_name,
            "BirthDate": birth_date,
            "BirthPlace": birth_place,
            "Nationallity": {"Code": nationality} if nationality else {},
            "Ethenic": {"Code": ethnic} if ethnic else {},
            "FamilyType": family_type,
        }

        if person_id:
            payload["id"] = person_id
            res_json = _call_person_api('/updatePersonbyPersonId', payload, cookies)
        else:
            res_json = _call_person_api('/addPerson', payload, cookies)
            person_id = (res_json.get('data') or {}).get('_id') or person_id

        status = res_json.get('status')
        msg = res_json.get('message') or ('Thành công' if status == 'OK' else 'Lỗi')
        # re-fetch to show latest data if success
        if status == 'OK' and person_id:
            return redirect(f"/person/detail?id={person_id}&msg={msg}")

        # fall-through to render form with message
        person_data = payload
        return render_template(
            'person_detail.html',
            title='Person detail',
            auth=True,
            person=person_data,
            message=msg,
            is_new=not person_id,
        )

    # GET: load person if id provided
    person_data = {}
    msg = request.args.get('msg')
    if person_id:
        res_json = _call_person_api('/getPersonInfobyPersonId', {"id": person_id}, cookies)
        if res_json.get('status') == 'OK':
            person_data = res_json.get('data') or {}
        else:
            msg = res_json.get('message', 'Không tải được thông tin')

    return render_template(
        'person_detail.html',
        title='Person detail',
        auth=True,
        person=person_data,
        message=msg,
        is_new=not person_id,
    )
