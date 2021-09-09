from app.api import rest_api, token_auth
from flask_restful import Resource, fields, marshal_with, reqparse
from app.models import Profile, Symptom, ProfileSymptom, UserAccessProfile
from flask import g
from app import db
import dateutil.parser

user_symptom_fields = {
    'id': fields.Integer,
    'intensity': fields.Integer,
    'marked_datetime': fields.String,
    'symptom': fields.Nested(
        {
            'id': fields.Integer,
            'name': fields.String,
        }
    )
}

symptom_fields = {
    'id': fields.Integer,
    'name': fields.String,
}


class SymptomCategoryApi(Resource):
    @token_auth.login_required
    @marshal_with(symptom_fields)
    def get(self):
        return Symptom.query.all()


class ProfileSymptomApi(Resource):
    @token_auth.login_required
    def delete(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        profile = Profile.query.get(profile_id)
        if not UserAccessProfile.check_has_access(user, profile):
            return {'success': False}, 400

        obj = ProfileSymptom.query.filter_by(
            profile_id=profile_id, id=args['id']).first()
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return {'success': True}, 200
        else:
            return {'message', 'Not found'}, 400

    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        parser.add_argument('date', type=str, required=True)
        parser.add_argument('symptom_id', type=str, required=True)
        parser.add_argument('intensity', type=str, required=True)
        args = parser.parse_args(strict=True)

        parsed_date = dateutil.parser.parse(args['date'])
        profile_id = args['profile_id']
        profile = Profile.query.get(profile_id)
        if not UserAccessProfile.check_has_access(user, profile):
            return {'success': False}, 400

        user = token_auth.current_user()
        profile_symptom = ProfileSymptom(
            profile_id=profile_id,
            sympton_id=args['symptom_id'],
            intensity=args['intensity'],
            marked_datetime=parsed_date)
        db.session.add(profile_symptom)
        db.session.commit()
        return {'success': True}, 200

    @token_auth.login_required
    @marshal_with(user_symptom_fields)
    def get(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('per_page', type=int, default=20)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        profile = Profile.query.get(profile_id)
        if not UserAccessProfile.check_has_access(user, profile):
            return {'success': False}, 400
            
        per_page = min(50, args['per_page'])
        return ProfileSymptom.query.filter_by(profile_id=profile_id).order_by(ProfileSymptom.marked_datetime.desc()).paginate(page=args['page'], per_page=per_page, error_out=False).items


rest_api.add_resource(ProfileSymptomApi, '/user_symptom')
rest_api.add_resource(SymptomCategoryApi, '/symptom_category')
