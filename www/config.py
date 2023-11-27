import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-fallback-secret-key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True 
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    # Other development-specific settings


class ProductionConfig(Config):
    PORT = 131
    DEBUG = False
    # Other production-specific settings

