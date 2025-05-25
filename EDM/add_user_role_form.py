from wtforms import (
    Form, SelectField, SubmitField, validators
)

from EDM.databae import get_user_roles

class AddUserRoleForm(Form):
    role = SelectField('Выберите роль')
    submit = SubmitField('Подтвердить')

    def __init__(self, *args, **kwargs):
        super(AddUserRoleForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in get_user_roles()]