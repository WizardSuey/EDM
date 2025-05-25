from wtforms import IntegerField, StringField, BooleanField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf import FlaskForm

from EDM.databae import get_counterparties, get_user_roles

class AddUserForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    second_name = StringField('Фамилия', validators=[Optional(), Length(max=100)])
    surname = StringField('Отчество', validators=[Optional(), Length(max=100)])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[Optional()])
    role = SelectField('Роль', validators=[DataRequired()])
    has_signature = BooleanField('Может ставить подписи?', default=False)
    add_employee = BooleanField('Может добавлять новых сотрудников?', default=False)
    organization = SelectField('Организация', validators=[DataRequired()])
    blocked = BooleanField('Заблокирован?', default=False)
    login = StringField('Логин', validators=[DataRequired(), Length(max=50)])
    email = StringField('Почта', validators=[DataRequired(), Length(max=80)])
    send_tin = BooleanField('Подтверждён организацией?', default=False)
    password = StringField('Пароль', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Подтвердить')

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.organization.choices = [(org.id, org.name) for org in get_counterparties()]
        self.role.choices = [(role.id, role.name) for role in get_user_roles()]