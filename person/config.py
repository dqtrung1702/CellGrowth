import redis
class Config(object):
        PERSON_IP = '0.0.0.0'
        PERSON_PORT = 8083
        PERSON_DEBUG_MODE = True
        SECRET_KEY = 'ERP-as-Services'
        SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        SESSION_TYPE = 'redis'
        SESSION_REDIS = redis.from_url('redis://10.14.119.41:6379')
        JWT_SECRET = 'ERP-as-Services'
        JWT_ALGORITHM = 'HS256'
        JWT_EXP_DELTA_SECONDS = 6000000
        MONGO_URI = 'mongodb://10.14.119.40:27017/test'
        UAA_URL = 'http://localhost:8081/'