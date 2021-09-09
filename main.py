from app import create_app, db, scheduler, admin, cli, flaskadmin
from app.models import ScheduledProfileMedication, MedicationTaken, Profile, UserAccessProfile, Medication, MedicationInventory
from app.auth.models import Permission, Role, User
import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
cli.register(app)
flaskadmin.register(admin, db)
scheduler.start()


@app.shell_context_processor  # Shell automatic imports
def make_shell_context():
    return {
        'db': db,
        'UserAccessProfile': UserAccessProfile,
        'Profile': Profile,
        'User': User,
        'Medication': Medication,
        'ScheduledUserMedication': ScheduledProfileMedication,
        'MedicationTaken': MedicationTaken,
        'Role': Role,
        'Permission': Permission,
        # 'es': app.elasticsearch,
        'MedicationInventory': MedicationInventory,
    }
