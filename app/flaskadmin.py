# Add admin account
from flask_login import current_user
from app.auth.models import User
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for

# Flask-Admin Extension


def register(admin, db):
    class AdminView(ModelView):
        column_display_pk = True

        def is_accessible(self):
            return current_user.is_authenticated and current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('auth.login'))

    admin.add_view(AdminView(User, db.session))
