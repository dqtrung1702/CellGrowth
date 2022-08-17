import redis
import os 
redis_url = os.getenv('REDISTOGO_URL', 'redis://10.14.119.41:6379')
conn = redis.from_url(redis_url)
from rq.job import Job

j = Job.fetch('31f4e06e-354c-4db8-9559-9f7a4655c427', connection=conn)
print(j.result)