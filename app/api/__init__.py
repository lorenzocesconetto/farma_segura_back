from flask import Blueprint
from flask import g
from app.auth.models import User
from app import db
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from .errors import error_response
from flask_restful import Api


bp = Blueprint('api', __name__)
rest_api = Api(bp)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

@token_auth.verify_token
def verify_token(token):
    return User.verify_auth_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)


from app.api import (user_medication, medication, 
auth, medication_taken, all_medications, pharmacist, symptom, inventory, 
autocomplete, profile, profile_access)


