from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length, Optional
from app.auth.models import User


class EditProfileForm(FlaskForm):
    name = StringField('Nome Completo', validators=[Length(1, 64)])
    cep = StringField('CEP (somente numeros)', validators=[
                      DataRequired(), Regexp(r'^\d{8}$', 0, 'CEP inválido'), Length(8, 8)])
    logradouro = StringField('Endereço', validators=[
                             DataRequired(), Length(2, 128)])
    complemento = StringField('Complemento', validators=[
                              Optional(), Length(1, 64)])
    bairro = StringField('Bairro', validators=[DataRequired(), Length(2, 64)])
    municipio = StringField('Cidade', validators=[
                            DataRequired(), Length(1, 64)])
    uf = StringField('UF', validators=[DataRequired(), Length(2, 2)])
    phone = StringField('Celular com DDD', validators=[DataRequired(), Regexp(
        r'^[0-9()\-.\s]{8,19}$', 0, 'Número inválido'), Length(10, 19)])
    submit = SubmitField('Alterar')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 128), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Manter-me logado', default=True)
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    name = StringField('Nome Completo', validators=[Length(1, 64)])
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 128), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Este email já foi cadastrado.')

    def validate_password(self, password):
        if len(password.data) < 7:
            raise ValidationError('A senha deve ter pelo menos 7 caracteres.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Redefinir senha')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField('Repita a Senha', validators=[DataRequired(),
                                                            EqualTo('password')])
    submit = SubmitField('Redefinir senha')
