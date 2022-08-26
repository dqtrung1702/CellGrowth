import redis
class Config(object):
        PERSON_IP = '0.0.0.0'
        PERSON_PORT = 8083
        PERSON_DEBUG_MODE = True
        SECRET_KEY = 'ERP-as-Services'
        SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        SESSION_TYPE = 'redis'
        SESSION_REDIS = redis.from_url('redis://10.14.119.41:6379')
        MONGO_URI = 'mongodb://root:pass12345@10.14.119.41:27018/test?authSource=admin'
        UAA_URL = 'http://localhost:8081/'