from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, DateField, TextAreaField, Form, SelectField

from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import DataRequired, Length

class TinForm(FlaskForm):
    tin = StringField('ИНН', validators=[DataRequired(), Length(max=12)])
    submit = SubmitField('Отправить')
