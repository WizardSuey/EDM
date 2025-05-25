from wtforms import IntegerField, StringField, BooleanField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf import FlaskForm

from EDM.databae import get_counterparties, get_user_roles

class AddCounterpartyForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=100)])
    tin = StringField('ИНН', validators=[DataRequired(), Length(max=12)])
    email = StringField('Почта', validators=[DataRequired(), Length(max=80)])
    phone_number = StringField('Телефон', validators=[DataRequired(), Length(max=15)])
    address = StringField('Адрес', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Подтвердить')