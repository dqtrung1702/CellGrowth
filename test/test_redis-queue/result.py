import redis
import os 
redis_url = os.getenv('REDISTOGO_URL', 'redis://10.14.119.41:6379')
conn = redis.from_url(redis_url)
from rq.job import Job

j = Job.fetch('ee0d406e-49ff-45bb-a4d8-c10022345797', connection=conn)
print(j.result)