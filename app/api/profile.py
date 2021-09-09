from app.models import Profile, UserAccessProfile
from flask_restful import fields, Resource, marshal_with, reqparse
from app.api import rest_api, token_auth
from app import db

profile_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String,
}


class UsernameApi(Resource):
    @token_auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        args = parser.parse_args(strict=True)
        username = args['username'].strip().lower()
        if Profile.query.filter_by(username=username).first():
            return False
        return True


class ProfileNotificationApi(Resource):
    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int, required=True)
        parser.add_argument('notifications_on', type=bool, required=True)
        args = parser.parse_args(strict=True)
        
        access = UserAccessProfile.query.filter_by(
            user_id=user.id, profile_id=args['profile_id']).first()
        if not access:
            return {'success': False}, 400

        access.notifications_on = args['notifications_on']
        db.session.commit()
        return {'success': True}, 200


class ProfileApi(Resource):
    @token_auth.login_required
    def delete(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int, required=True)
        args = parser.parse_args(strict=True)

        profile = Profile.query.filter_by(id=args['profile_id']).first()

        if profile and UserAccessProfile.check_is_owner(user=user, profile=profile):
            db.session.delete(profile)
            db.session.commit()
            return {'success': True}, 200
        else:
            access = UserAccessProfile.query.filter_by(
                user_id=user.id, profile_id=args['profile_id']).first()
            if access:
                db.session.delete(access)
                return {'success': True}, 200
            return {'message': 'Not found'}, 404

    @token_auth.login_required
    def get(self):
        user = token_auth.current_user()
        return [x.to_dict() for x in UserAccessProfile.query.filter_by(user_id=user.id)]

    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, required=True)
        parser.add_argument('last_name', type=str, required=True)
        parser.add_argument('cpf', type=int, required=True)
        parser.add_argument('username', type=str, required=True)
        args = parser.parse_args(strict=True)

        username = args['username'].strip().lower()
        profile = Profile.query.filter_by(username=username).first()
        if profile:
            return {'success': False, 'message': 'Este nome de usuário já está sendo utilizado'}, 400
        profile = Profile(
            first_name=args['first_name'],
            last_name=args['last_name'],
            cpf=args['cpf'],
            username=username,
        )
        db.session.add(profile)
        db.session.commit()
        user_access_profile = UserAccessProfile(
            user_id=user.id, profile_id=profile.id, is_owner=True)
        db.session.add(user_access_profile)
        db.session.commit()
        return {'success': True, 'data': user_access_profile.to_dict()}, 200


rest_api.add_resource(ProfileNotificationApi, '/profile_notification')
rest_api.add_resource(ProfileApi, '/profile')
rest_api.add_resource(UsernameApi, '/username_check')
