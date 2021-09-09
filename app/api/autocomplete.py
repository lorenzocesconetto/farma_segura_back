from sqlalchemy import and_
from flask_restful import Resource, reqparse, fields, marshal_with
from app.models import Medication, MedicationInventory, MedicationTaken, ScheduledProfileMedication
from app.api import token_auth, rest_api


autocomplete_fields = {
    'id': fields.Integer,
    'nome_comercial': fields.String,
    'apresentacao': fields.String,
    'razao_social': fields.String,
    'principios_ativos': fields.String,
}


class AutocompleteApi(Resource):
    @token_auth.login_required
    @marshal_with(autocomplete_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str,
                            help='Provide a query', required=True)
        parser.add_argument('num_suggestions', type=int,
                            help='Provide number of suggestions', required=True)
        args = parser.parse_args(strict=True)

        query = args['query']
        if len(query) < 2:
            return []
        num_suggestions = args['num_suggestions']
        # Tokenize + Add wild card
        query_terms = query.split()
        tsquery = " & ".join(query_terms)
        # tsquery += ":*"
        # tsquery += "*"
        return Medication.query.filter(Medication.__ts_vector__.match(tsquery, postgresql_regconfig='portuguese')).all()[:num_suggestions]
        # return Medication.query.filter(Medication.__ts_vector__.match(tsquery)).all()[:num_suggestions]
        # return Medication.query.filter(Medication.__ts_vector__.match(tsquery, postgresql_regconfig='portuguese')).all()[:num_suggestions]


rest_api.add_resource(AutocompleteApi, '/autocomplete')
