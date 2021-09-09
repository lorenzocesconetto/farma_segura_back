from app import db
from flask_migrate import upgrade
from flask import current_app
from app.models import Medication, Symptom, Pharmacist


def register(app):
    @app.cli.command()
    def deploy():
        """Run deployment tasks."""
        print('Upgrading database to lastest migration...')
        upgrade()
        print('Done!')

        print('Adding symptoms...')
        Symptom.insert_symptoms()
        print('Done!')

        print('Adding pharmacists...')
        Pharmacist.insert_pharmacists()
        print('Done!')

        print('Adding medications...')
        Medication.insert_medications()
        print('Done!')
