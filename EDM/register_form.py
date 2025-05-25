from wtforms import IntegerField, StringField, BooleanField, DateField, SubmitField, SelectField, PasswordField, Form
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf import FlaskForm


class RegisterForm(Form):
    name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    second_name = StringField('Фамилия', validators=[Optional(), Length(max=100)])
    surname = StringField('Отчество', validators=[Optional(), Length(max=100)])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[Optional()])
    login = StringField('Логин', validators=[DataRequired(), Length(max=50)])
    email = StringField('Почта', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Подтвердить')