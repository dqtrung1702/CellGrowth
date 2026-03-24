import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Engine/Session sẽ được cấu hình qua container; fallback lấy từ env để tránh phụ thuộc trực tiếp Config.
engine = None
SessionLocal = None
Base = declarative_base()


def configure_engine(uri: str):
    global engine, SessionLocal
    engine = create_engine(uri, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# Fallback tự cấu hình nếu container chưa gọi configure_engine
_default_uri = os.getenv("UAA_DATABASE_URI", "postgresql://admin:admin@localhost:5432/dev?options=-c%20search_path=uaa")
configure_engine(_default_uri)


def get_session():
    if SessionLocal is None:
        raise RuntimeError("SessionLocal is not configured")
    return SessionLocal()
