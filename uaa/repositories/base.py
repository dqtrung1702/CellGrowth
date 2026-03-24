from contextlib import contextmanager

from models.database import db


class PostgresRepo:
    """Lightweight base repo that manages connection lifecycle from the db pool."""

    def __init__(self, db_instance=None):
        self._db = db_instance or db()

    @contextmanager
    def conn(self):
        conn = self._db.conn_pool.getconn()
        try:
            yield conn
        finally:
            self._db.conn_pool.putconn(conn)
