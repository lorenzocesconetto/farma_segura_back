from flask_restful import Resource, marshal_with, reqparse
from app.api import token_auth, rest_api
from app.models import Profile, UserAccessProfile
from app import db
from app.auth.models import User


class ProfileAccessApi(Resource):
    @token_auth.login_required
    def get(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int, required=True,
                            help='Provide the profile_id argument')
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        access = UserAccessProfile.query.filter_by(
            user_id=user.id, profile_id=profile_id, is_owner=True).first()
        if not access:
            return {'success': False, 'message': 'Você não tem autorização para ver este perfil'}
        return [x.user.to_dict() for x in Profile.query.get(profile_id).users if not x.is_owner]

    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int, required=True)
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args(strict=True)

        new_user = User.query.filter_by(email=args['email']).first()
        if not new_user:
            return {'success': False, 'message': 'Usuário não cadastrado'}, 400

        user_access = UserAccessProfile.query.filter_by(
            user_id=user.id, profile_id=args['profile_id'], is_owner=True).first()
        if not user_access:
            return {'success': False, 'message': 'Você não tem permissão'}, 400

        new_user_access = UserAccessProfile.query.filter_by(
            user_id=new_user.id, profile_id=args['profile_id']).first()
        if new_user_access:
            return {'success': False, 'message': 'Usuário já possui acesso a este perfil'}, 400

        new_user_access = UserAccessProfile(
            user_id=new_user.id, profile_id=args['profile_id'], is_owner=False)
        db.session.add(new_user_access)
        db.session.commit()
        return {'success': True}, 200

    @token_auth.login_required
    def delete(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int, required=True)
        parser.add_argument('user_id', type=int, required=True)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        access = UserAccessProfile.query.filter_by(
            user_id=user.id, profile_id=profile_id, is_owner=True).first()
        if not access:
            return {'success': False, 'message': 'Você não tem autorização para ver este perfil'}, 400
        access = UserAccessProfile.query.filter_by(
            user_id=args['user_id'], profile_id=profile_id).first()
        db.session.delete(access)
        db.session.commit()
        return {'success': True}, 200


rest_api.add_resource(ProfileAccessApi, '/profile_access')
