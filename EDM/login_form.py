from wtforms import (
    Form, BooleanField, StringField, PasswordField, validators
)


class LoginForm(Form):
    login = StringField(None, [
        validators.DataRequired()
        ])
    password = PasswordField(None, [
        validators.DataRequired()
    ])