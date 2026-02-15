import redis
from datetime import timedelta
class Config(object):
        UAA_IP = '0.0.0.0'
        UAA_PORT = 8082
        UAA_DEBUG_MODE = True

        POSTGRES_HOST = "127.0.0.1"
        POSTGRES_PORT = "5432"
        POSTGRES_DB = "dev"
        POSTGRES_USERNAME = "admin"
        POSTGRES_PASSWORD = "admin"
        POSTGRES_OPTIONS = "-c search_path=dbo,uaa"
        POSTGRES_MINCONN= 1
        POSTGRES_MAXCONN= 10

        SECRET_KEY = 'ERP-as-Services'
        SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        SESSION_TYPE = 'redis'
        SESSION_REDIS = redis.from_url('redis://127.0.0.1:6379')
        PERMANENT_SESSION_LIFETIME = timedelta(hours=12)

        JWT_SECRET = '$2a$12$hUXgiU2qN/ELnVASgsti1ujEZVbGtpeyPEkddJR4vbrnfSyzdaJaW'
        JWT_ALGORITHM = 'HS256'
        JWT_EXP_DELTA_SECONDS = 6000000

        SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5432/dev?options=-c%20search_path=uaa'
        SQLALCHEMY_TRACK_MODIFICATIONS = True

        UAA_URL = 'http://localhost:8082/'
        BOOLEAN = {'False':False,'True':True,'false':False,'true':True,'on':True,'off':False}
