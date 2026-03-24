from contextlib import contextmanager

from sqlalchemy import text

from models.orm import SessionLocal


class OrmRepo:
    """Base repository using SQLAlchemy session (future=True)."""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    @contextmanager
    def session(self):
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # Convenience wrapper for text queries
    def execute(self, session, sql: str, params=None):
        return session.execute(text(sql), params or {})

    def _bind_sql(self, sql: str, params):
        """
        Convert psycopg-style %s placeholders to named binds (:p0, :p1, ...)
        and return (sql, dict_params).
        """
        if not params:
            return sql, {}
        bound = {}
        parts = sql.split("%s")
        rebuilt = []
        for i, part in enumerate(parts):
            rebuilt.append(part)
            if i < len(parts) - 1:
                key = f"p{i}"
                rebuilt.append(f":{key}")
                bound[key] = params[i]
        return "".join(rebuilt), bound
