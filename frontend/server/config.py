from os import environ
class Config(object):
    SECRET_KEY = 'ERP-as-Services'
    JWT_SECRET = '$2a$12$hUXgiU2qN/ELnVASgsti1ujEZVbGtpeyPEkddJR4vbrnfSyzdaJaW'
    JWT_ALGORITHM = 'HS256'
    DEFAULT_THEME = None
    UAA_URL = 'http://localhost:8082'
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
