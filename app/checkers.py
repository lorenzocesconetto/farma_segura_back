from app.auth.models import User
from wtforms.validators import Email
import email_validator
import re


def check_phone(s):
    if not bool(re.match(r'^[0-9()\-.\s]{10,19}$', s)) or len(s) > 19 or len(s) < 10:
        raise ValueError("Campo telefone invalido")
    return s


def exact_length(length):
    def validate(s):
        if len(s) == length:
            return s
        raise ValueError(f"Campo deve ter exatamente {length} caracteres")
    return validate


def min_length(length):
    def validate(s):
        if len(s) >= length:
            return s
        raise ValueError(f"Campo deve ter pelo menos {length} caracteres")
    return validate


def check_email_unique(val):
    check_email(val)
    if User.query.filter_by(email=val).first():
        raise ValueError('Este email já foi cadastrado.')
    return val


def check_email(val):
    email_checker = CheckEmail()
    return email_checker.is_valid(val)


class CheckEmail(Email):
    def is_valid(self, field):
        try:
            if field is None:
                raise ValueError('Email invalido')
            email_validator.validate_email(
                field,
                check_deliverability=self.check_deliverability,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
            )
            return field
        except email_validator.EmailNotValidError as e:
            raise ValueError('Email invalido')
