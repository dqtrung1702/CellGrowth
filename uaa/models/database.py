
from config import Config
from psycopg2.pool import SimpleConnectionPool


class db:
    """Light wrapper around psycopg2 connection pool."""

    def __init__(self):
        self.conn_pool = SimpleConnectionPool(
            Config.POSTGRES_MINCONN,
            Config.POSTGRES_MAXCONN,
            host=Config.POSTGRES_HOST,
            database=Config.POSTGRES_DB,
            user=Config.POSTGRES_USERNAME,
            password=Config.POSTGRES_PASSWORD,
            port=Config.POSTGRES_PORT,
            options=Config.POSTGRES_OPTIONS,
        )

    def start_op(self):
        """Get a connection + cursor; caller must return the connection via close_op."""
        conn = self.conn_pool.getconn()
        cur = conn.cursor()
        return conn, cur

    def close_op(self, conn):
        conn.commit()
        self.conn_pool.putconn(conn)
