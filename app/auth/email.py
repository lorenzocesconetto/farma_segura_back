from flask import render_template, current_app
from app.email import send_email
from app.constants import FORGOT_PASSWORD_TOKEN_EXPIRATION_SECONDS


def send_password_reset_email(user):
    token = user.get_reset_password_token(
        FORGOT_PASSWORD_TOKEN_EXPIRATION_SECONDS)
    send_email('[BuscaMed] Definição de Nova Senha',
               sender=current_app.config['FLASKY_MAIL_SENDER'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_email_confirmation_email(user):
    token = user.get_email_confirmation_token()
    send_email('[BuscaMed] Confirmação de email',
               sender=current_app.config['FLASKY_MAIL_SENDER'],
               recipients=[user.email],
               text_body=render_template('email/email_confirmation.txt',
                                         user=user, token=token),
               html_body=render_template('email/email_confirmation.html',
                                         user=user, token=token))
