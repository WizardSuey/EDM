from wtforms import (
    Form, SelectField, SubmitField, validators
)


class SelectCreateDocumentForm(Form):
    document_type = SelectField('выберите тип', choices=[
        ('УПД'),
        ('Договор')
    ])
    submit = SubmitField('Создать')