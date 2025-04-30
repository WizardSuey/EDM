from wtforms import (
    Form, BooleanField, StringField, PasswordField, validators
)


class LoginForm(Form):
    login = StringField("Логин", [
        validators.DataRequired()
        ])
    password = PasswordField("Пароль", [
        validators.DataRequired()
    ])