from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
import os
from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(
        current_app._get_current_object(), msg)).start()


def sendgrid_email():
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python
    message = Mail(
        from_email='lorenzo_cesconeto@hotmail.com',
        to_emails='lorenzo.cesconeto@gmail.com',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<p>Testing this out. Its <strong>easy to do anywhere, even with Python</strong></p>'
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
