from flask import g
from flask_restful import Resource, reqparse, fields, marshal_with
from app.checkers import check_email, check_email_unique, check_phone, exact_length, min_length
from app.auth.models import User
from app import db
from app.auth.email import send_password_reset_email, send_email_confirmation_email
from datetime import datetime, timedelta
from app.helpers import simple_utc
from app.constants import ACCESSS_TOKEN_EXPIRATION_SECONDS
from app.api import rest_api, basic_auth


def get_expriration_date(seconds):
    if seconds is None:
        return None
    expiration_datetime = datetime.utcnow(
    ) + timedelta(seconds=ACCESSS_TOKEN_EXPIRATION_SECONDS)
    return simple_utc.add_utc_info(expiration_datetime)


class Login(Resource):
    @basic_auth.login_required
    def post(self):
        user = basic_auth.current_user()
        expiration_string = get_expriration_date(
            ACCESSS_TOKEN_EXPIRATION_SECONDS)
        return {'token': user.generate_auth_token(ACCESSS_TOKEN_EXPIRATION_SECONDS), 'expiration': expiration_string, 'user_id': user.id}


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str,
                            help='Provide a valid first name', required=True)
        parser.add_argument('last_name', type=str,
                            help='Provide a valid last name', required=True)
        parser.add_argument('email', type=check_email,
                            help='Provide a valid account email', required=True)
        parser.add_argument(
            'cpf', type=str, help='Provide a valid cpf', required=True)
        parser.add_argument('password', type=min_length(
            7), help='Provide the account password', required=True)
        args = parser.parse_args(strict=True)
        user = User.query.filter_by(email=args['email']).first()
        if user:
            return {
                'message': "Email já cadastrado na plataforma"
            }, 400
        user = User(
            first_name=args['first_name'],
            last_name=args['last_name'],
            email=args['email'],
            cpf=args['cpf'],
        )
        user.set_password(args['password'])
        db.session.add(user)
        db.session.commit()
        # send_email_confirmation_email(user)
        expiration_string = get_expriration_date(
            ACCESSS_TOKEN_EXPIRATION_SECONDS)
        return {'success': True, 'token': user.generate_auth_token(ACCESSS_TOKEN_EXPIRATION_SECONDS), 'expiration': expiration_string, 'user_id': user.id}, 200


class ForgotPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=check_email,
                            help='Provide a valid account email', required=True)
        args = parser.parse_args(strict=True)
        user = User.query.filter_by(email=args['email']).first()
        if user:
            send_password_reset_email(user)
        return {'success': True}, 200


rest_api.add_resource(Login, '/token')
rest_api.add_resource(Register, '/register')
rest_api.add_resource(ForgotPassword, '/forgot_password')
