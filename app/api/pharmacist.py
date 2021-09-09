from app.api import rest_api, token_auth
from flask_restful import Resource, fields, marshal_with
from app.models import Pharmacist
from flask import g

pharmacist_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'whatsapp_number': fields.String,
    'role': fields.String,
    'profile_pic_url': fields.String,
}


class PharmacistApi(Resource):
    @token_auth.login_required
    @marshal_with(pharmacist_fields)
    def get(self):
        return Pharmacist.query.all()


rest_api.add_resource(PharmacistApi, '/pharmacists')
