from logging import DEBUG
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '587')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in [
        'true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['lorenzo_cesconeto@hotmail.com']
    DELIVERY_EMAILS = ['lorenzo_cesconeto@hotmail.com']
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    ITEMS_PER_PAGE = 24
    SCHEDULER_API_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ELASTICSEARCH_URL = os.environ.get('DEV_ELASTICSEARCH_URL')
    SCRAPYRT_URL = os.environ.get('DEV_SCRAPYRT_URL')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL') or 'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SCRAPYRT_URL = os.environ.get('SCRAPYRT_URL')


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig,
}
