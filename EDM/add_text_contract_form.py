from wtforms import SubmitField, Form
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

class ContractDocumentForm(Form):
    text = CKEditorField('Текст Договора', validators=[DataRequired()])
    submit = SubmitField('Подписать')
