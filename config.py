import os


class Config(object):
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key'
    RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST') or 'localhost'
    ASP_API_URL = "http://localhost:5000/api"
    API_KEY = 'YOUR_API_KEY'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
