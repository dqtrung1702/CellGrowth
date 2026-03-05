from datetime import datetime
import re

from flask import Blueprint

# Shared blueprint and helpers for permission-related routes
permission = Blueprint(
    'permission_blueprint',
    __name__,
)


def _fmt_dt(val):
    """Convert various datetime representations (dict/$date, datetime, str, None) to string for UI."""
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
        return datetime.fromisoformat(s.replace('Z', '+00:00')).date().isoformat()
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


# Attach route groups
from . import role  # noqa: F401,E402
from . import data  # noqa: F401,E402
