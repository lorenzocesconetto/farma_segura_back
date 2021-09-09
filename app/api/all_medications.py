from sqlalchemy import and_
from flask_restful import Resource, reqparse, fields, marshal_with
from app.models import MedicationInventory, MedicationTaken, Profile, ScheduledProfileMedication, UserAccessProfile
from flask import current_app
from app import db
import datetime
import dateutil.parser
from app.api import medication, token_auth, rest_api

all_medications_fields = {
    'id': fields.Integer,
    'medication': fields.Nested({
        'id': fields.Integer,
        'nome_comercial': fields.String,
        'apresentacao': fields.String,
    }),
    'quantity': fields.Integer,
    'original_timestamp': fields.String,
    'taken': fields.Boolean,
    'inventory': fields.Float,
}


class AllMedicationsApi(Resource):
    @token_auth.login_required
    @marshal_with(all_medications_fields)
    def get(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument(
            'date', type=str, help='Provide a date', required=True)
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        args = parser.parse_args(strict=True)
        parsed_date = dateutil.parser.parse(args['date'])
        min_date = datetime.datetime.combine(
            parsed_date.date(), datetime.datetime.min.time())
        max_date = min_date + datetime.timedelta(days=1)

        profile_id = args['profile_id']
        if not UserAccessProfile.query.filter_by(user_id=user.id, profile_id=profile_id).first():
            return {'success': False}, 400

        return_data = []
        lookup = set()
        for med in MedicationTaken.get_history(profile_id=profile_id, max_date=max_date, min_date=min_date):
            lookup.add((med.medication_id, med.original_timestamp))
            dict_data = med.to_dict()
            dict_data['original_timestamp'] = dict_data['original_timestamp'].isoformat()
            inventory = MedicationInventory.query.filter_by(
                profile_id=profile_id, medication_id=dict_data['medication']['id']).first()
            if inventory:
                dict_data['inventory'] = inventory.inventory
            else:
                dict_data['inventory'] = None
            return_data.append(dict_data)

        for med in ScheduledProfileMedication.query.filter_by(profile_id=profile_id).all():
            next_date = med.get_next_scheduled(parsed_date)
            if (med.medication_id, next_date) in lookup:
                continue
            if next_date and next_date >= min_date and next_date < max_date:
                inventory = MedicationInventory.query.filter_by(
                    profile_id=profile_id, medication_id=med.medication_id).first()
                if inventory:
                    inv = inventory.inventory
                else:
                    inv = None
                return_data.append(
                    {**med.to_dict(), 'taken': None, 'original_timestamp': next_date.isoformat(), 'inventory': inv})
        return_data.sort(key=lambda x: x['original_timestamp'])
        return return_data


rest_api.add_resource(AllMedicationsApi, '/all_medications')
