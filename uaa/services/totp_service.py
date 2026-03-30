import pyotp
from typing import Optional, Dict

from models.orm import SessionLocal
from models.entities import UserTOTP


class TOTPService:
    def __init__(self, session_factory=SessionLocal):
        self.session_factory = session_factory

    def enroll(self, user_id: int) -> Dict:
        secret = pyotp.random_base32()
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=str(user_id), issuer_name="UAA")
        with self.session_factory() as session:
            rec = session.get(UserTOTP, user_id)
            if rec:
                rec.secret_base32 = secret
                rec.confirmed = False
            else:
                rec = UserTOTP(user_id=user_id, secret_base32=secret, confirmed=False)
                session.add(rec)
            session.commit()
        return {"secret": secret, "provisioning_uri": uri}

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

    def disable(self, user_id: int):
        with self.session_factory() as session:
            rec = session.get(UserTOTP, user_id)
            if rec:
                session.delete(rec)
                session.commit()

