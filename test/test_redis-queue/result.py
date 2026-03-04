import os
import redis
from rq.job import Job

redis_url = (
    os.getenv('RQ_REDIS_URL')
    or os.getenv('REDISTOGO_URL')
    or os.getenv('REDIS_URL')
    or 'rediss://:change-me@localhost:6380/14'
)
conn = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)

j = Job.fetch('31f4e06e-354c-4db8-9559-9f7a4655c427', connection=conn)
print(j.result)
