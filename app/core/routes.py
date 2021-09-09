from datetime import datetime
from flask import render_template, g, redirect, current_app, request, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.core import bp
from app.auth.models import Permission
from app.decorators import permission_required, admin_required


@bp.before_app_request
def before_request():
    # g.search_form = SearchForm()
    if current_user.is_authenticated:
        current_user.ping()


@bp.get('/')
def index():
    return render_template('core/index.html')


@bp.get('/protected')
@login_required
def protected():
    return render_template('core/index.html')
