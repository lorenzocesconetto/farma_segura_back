from flask_restful import Resource, reqparse, fields
from app.models import MedicationInventory, ScheduledProfileMedication, UserAccessProfile
from app import db
from app.api import rest_api, token_auth

scheduled_user_medication_fields = {
    'id': fields.Integer,
    'medication': fields.Nested({
        'id': fields.Integer,
        'nome_comercial': fields.String,
        'apresentacao': fields.String,
    }),
    'cron_schedule': fields.String,
    'quantity': fields.Integer,
    'minute': fields.Integer,
    'hour': fields.Integer,
    'message': fields.String,
}


class ScheduledUserMedicationApi(Resource):
    @token_auth.login_required
    def delete(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args(strict=True)

        obj = ScheduledProfileMedication.query.get(args['id'])
        if not UserAccessProfile.check_has_access(user, obj.profile):
            return {'success': False}, 400
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return {'success': True}, 200
        else:
            return {'message', 'Not found'}, 400

    @token_auth.login_required
    def get(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        if not UserAccessProfile.query.filter_by(user_id=user.id, profile_id=profile_id).first():
            return {'success': False}, 400

        results = []
        for item in ScheduledProfileMedication.query.filter_by(profile_id=profile_id).all():
            results.append(item.to_dict())
        return results

    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        parser.add_argument('medication_id', type=int, required=True)
        parser.add_argument('frequency_scheduled', type=str, required=True)
        parser.add_argument('hour', type=int, required=True)
        parser.add_argument('minute', type=int, required=True)
        parser.add_argument('quantity', type=int, required=True)
        parser.add_argument('inventory', type=int)
        args = parser.parse_args(strict=True)

        profile_id = args['profile_id']
        if not UserAccessProfile.query.filter_by(user_id=user.id, profile_id=profile_id).first():
            return {'success': False}, 400

        assert args['minute'] >= 0
        assert args['minute'] <= 59
        assert args['hour'] >= 0
        assert args['hour'] <= 23

        frequency_scheduled = args['frequency_scheduled']
        if frequency_scheduled == 'everyday':
            cron_string = f"{args['minute']} {args['hour']} * * *"
        # elif frequency_scheduled == 'every_other_day':
        #     cron_string = f"{args['minute']} {args['hour']} */2 * *"
        else:
            raise Exception('Invalid frequency argument')

        medication_item = ScheduledProfileMedication(profile_id=profile_id,
                                                     medication_id=args['medication_id'],
                                                     cron_schedule=cron_string,
                                                     quantity=args['quantity'])
        db.session.add(medication_item)
        if args['inventory'] is not None:
            inventory_item = MedicationInventory.query.filter_by(
                profile_id=profile_id, medication_id=args['medication_id']).first()
            if inventory_item:
                inventory_item.inventory = args['inventory']
            else:
                inventory_item = MedicationInventory(profile_id=profile_id,
                                                     medication_id=args['medication_id'],
                                                     inventory=args['inventory'])
            db.session.add(inventory_item)
        db.session.commit()
        response = {'success': True,
                    'user_medication': medication_item.to_dict(), 'inventory': None}
        if args['inventory'] is not None and inventory_item:
            return {**response, 'inventory': inventory_item}, 200
        return response, 200


rest_api.add_resource(ScheduledUserMedicationApi, '/user_medication')
