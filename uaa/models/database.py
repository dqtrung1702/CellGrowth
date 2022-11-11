
from config import Config
from psycopg2.pool import SimpleConnectionPool

class db():
    # def __init__(self, xuser=Config.POSTGRES_USERNAME,xpassword=Config.POSTGRES_PASSWORD,xhost=Config.POSTGRES_HOST,xdatabase=Config.POSTGRES_DB,xport=Config.POSTGRES_PORT,xconnmin = Config.POSTGRES_MINCONN,xconnmax = Config.POSTGRES_MAXCONN):
    def __init__(self):
        self.dbConfig = Config
        self.conn_pool = SimpleConnectionPool(
            dbConfig.POSTGRES_MINCONN,
            dbConfig.POSTGRES_MAXCONN,
            host=dbConfig.POSTGRES_HOST,
            database=dbConfig.POSTGRES_DB,
            user=dbConfig.POSTGRES_USERNAME,
            password=dbConfig.POSTGRES_PASSWORD,
            port=dbConfig.POSTGRES_PORT
            )
        if (self.conn_pool):
            print("Connection pool created successfully using ThreadedConnectionPool")
    
    def get_cursor(self):
        conn = self.conn_pool.getconn()
        try:
            yield conn.cursor()
            conn.commit()
        finally:
            self.conn_pool.putconn(conn)

    def start_op(self):
        conn = self.conn_pool.getconn()
        cur = conn.cursor()
        return (conn, cur)
    
    def close_op(self, conn):
        conn.commit()
        self.conn_pool.putconn(conn)