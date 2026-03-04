import os
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']
redis_url = (
    os.getenv('RQ_REDIS_URL')
    or os.getenv('REDISTOGO_URL')
    or os.getenv('REDIS_URL')
    or 'rediss://:change-me@localhost:6380/14'
)
conn = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        # worker = Worker(Queue('default'))
        worker.work()
