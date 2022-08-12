import redis
import os 
redis_url = os.getenv('REDISTOGO_URL', 'redis://10.14.119.41:6379')
conn = redis.from_url(redis_url)
from rq.job import Job

j = Job.fetch('da749ec7-6e44-44cd-83a2-019e56c51ad7', connection=conn)
print(j.result)