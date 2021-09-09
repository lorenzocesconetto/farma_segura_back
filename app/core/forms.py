from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, FloatField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length, Optional

