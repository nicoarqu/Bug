import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    FLASK_APP= os.environ.get('FLASK_APP')
    FLASK_ENV= os.environ.get('FLASK_ENV')
    FLASK_DEBUG= os.environ.get('FLASK_DEBUG')
    ADMIN= os.environ.get('ADMIN')
    RECAPTCHA_PUBLIC_KEY= os.environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY= os.environ.get('RECAPTCHA_PRIVATE_KEY')
    DATABASE_URL= os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    DATABASE_URI= os.environ.get('DATABASE_URL').replace("://", "ql://", 1)


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True