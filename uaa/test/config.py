class Config(object):
        JWT_SECRET = 'ERP-as-Services'
        JWT_ALGORITHM = 'HS256'
        JWT_EXP_DELTA_SECONDS = 6000000
        SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin@localhost:5436/dev'
        SQLALCHEMY_TRACK_MODIFICATIONS = True
        UAA_URL = 'http://localhost:8081/'
        BOOLEAN = {'False':False,'True':True,'false':False,'true':True,'on':True,'off':False}