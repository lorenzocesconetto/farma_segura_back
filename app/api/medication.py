# from flask_restful import Resource, reqparse, fields, marshal_with
# from app.models import Medication, ScheduledUserMedication
# from flask import current_app
# from app import db
# from app.api import rest_api, token_auth


# scheduled_user_medication_fields = {
#     'description': fields.String,
#     'name': fields.String,
#     'laboratory': fields.String,
#     'active_principle': fields.String,
#     'price': fields.Float,
#     'ms_registry': fields.Integer,
#     'requires_prescription': fields.Boolean,
#     'ean': fields.Integer,
# }


# class MedicationApi(Resource):
#     @token_auth.login_required
#     @marshal_with(scheduled_user_medication_fields)
#     def get(self):
#         return Medication.query.all()

#     @token_auth.login_required
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('name', type=str, required=True)
#         parser.add_argument('description', type=str)
#         parser.add_argument('laboratory', type=str)
#         parser.add_argument('active_principle', type=str)
#         parser.add_argument('price', type=float)
#         parser.add_argument('ms_registry', type=int)
#         parser.add_argument('requires_prescription', type=bool, required=True)
#         parser.add_argument('ean', type=int)
#         args = parser.parse_args(strict=True)
#         med = Medication(description=args['description'],
#                          name=args['name'],
#                          laboratory=args['laboratory'],
#                          active_principle=args['active_principle'],
#                          price=args['price'],
#                          ms_registry=args['ms_registry'],
#                          requires_prescription=args['requires_prescription'],
#                          ean=args['ean'])
#         db.session.add(med)
#         db.session.commit()
#         return {'success': True, 'id': med.id}, 200


# rest_api.add_resource(MedicationApi, '/medication')
