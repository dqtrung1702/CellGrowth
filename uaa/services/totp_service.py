import pyotp
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

from models.orm import SessionLocal
from models.entities import UserTOTP
from config import Config


class TOTPService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def enroll(self, user_id: int) -> Dict:
        with self.session_factory() as session:
            rec = session.get(UserTOTP, user_id)
            # Nếu đã xác thực, không tạo secret mới (tránh thay đổi ngoài ý muốn)
            if rec and rec.confirmed and rec.secret_base32:
                return {"already_enabled": True, "confirmed": True}

            secret = rec.secret_base32 if rec and rec.secret_base32 else pyotp.random_base32()
            uri = pyotp.totp.TOTP(secret).provisioning_uri(name=str(user_id), issuer_name="UAA")

            if rec:
                rec.secret_base32 = secret
                rec.confirmed = False
            else:
                rec = UserTOTP(user_id=user_id, secret_base32=secret, confirmed=False)
                session.add(rec)
            session.commit()
        return {"secret": secret, "provisioning_uri": uri, "already_enabled": False}

    def verify(self, user_id: int, code: str) -> bool:
        if not code:
            return False
        with self.session_factory() as session:
            rec = session.get(UserTOTP, user_id)
            if not rec or not rec.secret_base32:
                return False
            totp = pyotp.TOTP(rec.secret_base32)
            ok = totp.verify(code, valid_window=1)
            if ok and not rec.confirmed:
                rec.confirmed = True
                session.commit()
            return ok

    def is_enabled(self, user_id: int) -> bool:
        with self.session_factory() as session:
            rec = session.get(UserTOTP, user_id)
            return bool(rec and rec.confirmed and rec.secret_base32)

    def verify_and_issue(self, mfa_token: str, code: str) -> Optional[Dict]:
        if not mfa_token:
            return None
        try:
            payload = jwt.decode(mfa_token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
            user_id = payload.get("UserId")
            username = payload.get("UserName") or str(user_id)
            if not payload.get("mfa") or not user_id:
                return None
        except Exception:
            return None
        if not self.verify(user_id, code):
            return None
        new_payload = {
            "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS),
            "UserId": user_id,
            "UserName": username,
        }
        token = jwt.encode(new_payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
        token_str = token if isinstance(token, str) else token.decode("utf-8")
        return {"token": token_str, "payload": new_payload}

    def disable(self, user_id: int):
        with self.session_factory() as session:
            rec = session.get(UserTOTP, user_id)
            if rec:
                session.delete(rec)
                session.commit()
