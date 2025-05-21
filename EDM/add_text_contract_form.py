from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField
from wtforms import SubmitField
from wtforms.validators import DataRequired

class ContractDocumentAddTextForm(FlaskForm):
    files = MultipleFileField('Текст Договора', validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG, JPG, JPEG files are allowed!')])
    submit = SubmitField('Подписать')
