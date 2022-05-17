from os import environ
class Config(object):
    SECRET_KEY = 'ERP-as-Services'
    JWT_SECRET = 'ERP-as-Services'
    JWT_ALGORITHM = 'HS256'
    DEFAULT_THEME = None
    UAA_URL = 'http://0.0.0.0:8081'
    PAGE_SIZE = 5

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
