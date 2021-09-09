from flask_restful import Resource, reqparse, fields
from app.models import MedicationInventory, MedicationTaken, Profile, UserAccessProfile
from app import db
import dateutil.parser
from app.api import token_auth, rest_api


medication_taken_fields = {
    'id': fields.Integer,
    'profile_id': fields.Integer,
    'medication_id': fields.Integer,
    'quantity': fields.String,
    'timestamp': fields.String,
    'taken': fields.Boolean,
}


class MedicationTakenApi(Resource):
    # @token_auth.login_required
    # @marshal_with(medication_taken_fields)
    # def get(self):
    #     user = token_auth.current_user()
    #     parser = reqparse.RequestParser()
    #     parser.add_argument('date', type=str, help='Provide a date', required=True)
    #     args = parser.parse_args(strict=True)
    #     parsed_date = dateutil.parser.parse(args['date'])
    #     min_date = parsed_date.date()
    #     return MedicationTaken.query.filter_by(user_id=user.id).filter(and_(MedicationTaken.original_timestamp >= min_date, MedicationTaken.original_timestamp < min_date + datetime.timedelta(days=1))).all()

    @token_auth.login_required
    def post(self):
        user = token_auth.current_user()
        parser = reqparse.RequestParser()
        parser.add_argument('medication_id', type=int, required=True)
        parser.add_argument('quantity', type=int, required=True)
        parser.add_argument('original_timestamp', type=str, required=True)
        parser.add_argument('taken', type=bool, required=True)
        parser.add_argument('profile_id', type=int,
                            help='Provide the profile id', required=True)
        args = parser.parse_args(strict=True)

        taken = args['taken']
        
        profile_id = args['profile_id']
        profile = Profile.query.get(profile_id)
        if not UserAccessProfile.check_has_access(user, profile):
            return {'success': False}, 400

        date = dateutil.parser.parse(args['original_timestamp'])
        item = MedicationTaken.query.filter_by(
            profile_id=profile_id, medication_id=args['medication_id'], original_timestamp=date).first()
        inventory = MedicationInventory.query.filter_by(
            profile_id=profile_id, medication_id=args['medication_id']).first()
        if item:
            if inventory and item.taken == False and taken == True:
                inventory.inventory -= args['quantity']
            if inventory and item.taken == True and taken == False:
                inventory.inventory += args['quantity']
            item.taken = taken
        elif not item:
            item = MedicationTaken(profile_id=profile_id,
                                   medication_id=args['medication_id'],
                                   quantity=args['quantity'],
                                   original_timestamp=date,
                                   taken=taken)
            if inventory and taken:
                inventory.inventory -= args['quantity']
            db.session.add(item)
        db.session.commit()
        return {'success': True}, 200


rest_api.add_resource(MedicationTakenApi, '/medication_taken')
