from flask_restful import Resource, reqparse, fields, marshal_with
from app.models import MedicationInventory, Profile, UserAccessProfile
from app import db
from app.api import rest_api, token_auth

inventory_medication = {
    'id': fields.Integer,
    'medication': fields.Nested(
        {
            'id': fields.Integer,
            'nome_comercial': fields.String,
            'apresentacao': fields.String,
        }
    ),
    'inventory': fields.Integer,
}


class MedicationInventoryApi(Resource):
    @token_auth.login_required
    def delete(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args(strict=True)

        obj = MedicationInventory.query.get(args['id'])
        if not UserAccessProfile.check_has_access(user, obj.profile):
            return {'success': False}, 400
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return {'success': True}, 200
        else:
            return {'message', 'Not found'}, 400

    @token_auth.login_required
    @marshal_with(inventory_medication)
    def get(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument(
            'profile_id', help='Provide a profile id', type=int, required=True)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        if not UserAccessProfile.query.filter_by(user_id=user.id, profile_id=profile_id).first():
            return {'success': False}, 400

        return MedicationInventory.query.filter_by(profile_id=profile_id).all()

    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('medication_id', type=int, required=True)
        parser.add_argument('initial_inventory', type=int, required=True)
        parser.add_argument(
            'profile_id', help='Provide a profile id', type=int, required=True)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        if not UserAccessProfile.query.filter_by(user_id=user.id, profile_id=profile_id).first():
            return {'success': False}, 400

        med_inv = MedicationInventory(
            medication_id=args['medication_id'],
            inventory=args['initial_inventory'],
            profile_id=profile_id,
        )
        db.session.add(med_inv)
        db.session.commit()
        return {'success': True}, 200


rest_api.add_resource(MedicationInventoryApi, '/medication_inventory')
