from flask import render_template, request, jsonify
from flask.helpers import flash
from app import db
from app.errors import bp


@bp.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    flash('Faça o login ou crie uma nova conta gratuitamente')
    return render_template('auth/login.html'), 403


@bp.app_errorhandler(404)
def not_found_error(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500


@bp.route('/error')
def error():
    return render_template('errors/500.html'), 500
