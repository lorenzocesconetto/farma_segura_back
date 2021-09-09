from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import EditProfileForm, LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.auth.models import User
from app.auth.email import send_password_reset_email, send_email_confirmation_email
from app.constants import *


@bp.get('/login')
@bp.post('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(form.password.data):
            flash(LOGIN_FAIL_MESSAGE)
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Entrar', form=form)


@bp.get('/edit_profile')
@bp.post('/edit_profile')
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.commit()
        flash(UPDATE_MESSAGE)
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.name.data = current_user.name
    return render_template('auth/edit_profile.html', title='Editar perfil', form=form)


@bp.get('/login_msg')
def login_msg():
    flash(LOGIN_MESSAGE)
    return redirect(url_for('auth.login'))


@bp.get('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.get('/register')
@bp.post('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User(email=email, name=form.name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_email_confirmation_email(user)
        flash(REGISTRATION_MESSAGE)
        login_user(user, remember=True)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.get('/reset_password_request')
@bp.post('/reset_password_request')
def reset_password_request():
    if current_user.is_authenticated:
        flash('Você já está logado')
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
        flash(RESET_PASSWORD_MESSAGE)
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.get('/reset_password/<token>')
@bp.post('/reset_password/<token>')
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(PASSWORD_CHANGE_MESSAGE)
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.get('/email_confirmation/<token>')
def email_confirmation(token):
    user = User.verify_email_confirmation_token(token)
    if user and not user.confirmed:
        login_user(user)
        user.confirmed = True
        db.session.commit()
        flash('Obrigado por confirmar seu email :)')
        return redirect(url_for('main.index'))
    elif user and user.confirmed:
        flash(EMAIL_ALREADY_CONFIRMED_MESSAGE)
    else:
        flash(FAIL_CONFIRM_EMAIL_MESSAGE)
    return redirect(url_for('auth.login'))
