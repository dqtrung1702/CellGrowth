class PasswordService:
    def hash(self, plain: str):
        try:
            import bcrypt  # lazy import để tránh crash nếu thiếu

            return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
        except Exception:
            return plain.encode("utf-8")

    def verify(self, stored, provided: str) -> bool:
        if stored is None:
            return False
        if isinstance(stored, memoryview):
            stored = stored.tobytes()
        elif isinstance(stored, bytearray):
            stored = bytes(stored)
        try:
            import bcrypt  # lazy import

            if isinstance(stored, (bytes, bytearray)):
                return bcrypt.checkpw(provided.encode("utf-8"), stored)
        except Exception:
            pass
        if isinstance(stored, bytes):
            try:
                return stored.decode("utf-8") == provided
            except Exception:
                return False
        return str(stored) == provided
