import json
from functools import wraps
from typing import Type, Any
from urllib.parse import urlencode

from flask import request, g
from werkzeug.wrappers import Response
from bson import json_util

try:  # optional import để hỗ trợ pydantic model làm payload
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    BaseModel = None


def _extract_meta(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get("meta")
    try:
        return getattr(obj, "meta", None)
    except Exception:
        return None


def json_response(payload, status: int = 200):
    if BaseModel and isinstance(payload, BaseModel):  # cho phép trả thẳng pydantic model
        payload = payload.model_dump(by_alias=True)
    headers = {}
    req_id = getattr(g, "request_id", None)
    if req_id:
        headers["X-Request-ID"] = req_id

    meta = _extract_meta(payload)
    if meta and isinstance(meta, dict) and "total" in meta:
        total = meta.get("total")
        page = meta.get("page", 1)
        page_size = meta.get("page_size", meta.get("pageSize", 10))
        headers["X-Total-Count"] = str(total) if total is not None else "0"
        links = []
        base_url = request.base_url
        q = request.args.to_dict(flat=False)
        q["page_size"] = [page_size]
        if page and page > 1:
            q["page"] = [page - 1]
            prev_url = f"{base_url}?{urlencode(q, doseq=True)}"
            links.append(f'<{prev_url}>; rel="prev"')
        if total is not None and page_size and page * page_size < total:
            q["page"] = [page + 1]
            next_url = f"{base_url}?{urlencode(q, doseq=True)}"
            links.append(f'<{next_url}>; rel="next"')
        if links:
            headers["Link"] = ", ".join(links)

    return Response(json.dumps(payload, default=json_util.default), mimetype="application/json", status=status, headers=headers)


def validate_body(model_cls: Type[Any]):
    """Decorator to validate JSON body with a pydantic model (extra fields allowed)."""
    try:
        from pydantic import ValidationError
    except Exception:  # pragma: no cover - import guard
        ValidationError = Exception

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            try:
                parsed = model_cls.model_validate(data)  # pydantic v2
            except AttributeError:
                try:
                    parsed = model_cls(**data)  # pydantic v1 fallback
                except Exception as exc:  # pragma: no cover
                    return json_response({"message": str(exc), "status": "FAIL"}, status=400)
            except ValidationError as exc:
                return json_response({"message": exc.errors(), "status": "FAIL"}, status=400)
            request.parsed_obj = parsed
            return fn(*args, **kwargs)
        return wrapper
    return decorator
