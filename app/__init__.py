import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from elasticsearch import Elasticsearch
from config import config
from flask_admin import Admin
from flask_admin.base import AdminIndexView
from flask_apscheduler import APScheduler
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login ou crie uma conta para acessar essa página.'
mail = Mail()
bootstrap = Bootstrap()
scheduler = APScheduler()


class IndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))


admin = Admin(name='BuscaMed', index_view=IndexView(),
              template_mode='bootstrap4')


def create_app(config_name: str):
    app = Flask(__name__)
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.config.from_object(config[config_name])

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    admin.init_app(app)
    scheduler.init_app(app)

    app.elasticsearch = Elasticsearch(
        [app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.core import bp as core_bp
    app.register_blueprint(core_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v0')

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='BuscaMed FAILURE',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/buscamed.log', maxBytes=10 ** 5, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('BuscaMed startup')

    return app

from app import models
from app.auth import models
