from wtforms import StringField, IntegerField, DecimalField, DateField, TextAreaField, Form, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, MultipleFileField

from EDM.databae import get_counterparties

class ContractDocumentForm(FlaskForm):
    number = StringField('Number', validators=[DataRequired(), Length(max=255)])
    counterparty = SelectField('Контрагент', validators=[DataRequired()])
    creator = IntegerField('Creator', validators=[DataRequired()])
    creator_counterparty = IntegerField('Creator Counterparty', validators=[DataRequired()])
    client = SelectField('Заказчик', validators=[DataRequired()])
    client_base = TextAreaField('Основание Заказчика', validators=[DataRequired()])
    provider = SelectField('Поставщик', validators=[DataRequired()])
    provider_base = TextAreaField('Основание Поставщика', validators=[DataRequired()])
    address = TextAreaField('Адрес', validators=[DataRequired()])
    document_type = IntegerField('Document Type', validators=[DataRequired()])
    document_status = IntegerField('Document Status', validators=[DataRequired()])
    sender_signature = IntegerField('Sender Signature')
    recipient_signature = IntegerField('Recipient Signature')
    date_of_receipt = DateField('Date of Receipt', format='%Y-%m-%d')
    files = MultipleFileField('Выберите файлы', validators=[FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG, JPG, JPEG files are allowed!')])
    file_path = TextAreaField('File Path', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(ContractDocumentForm, self).__init__(*args, **kwargs)
        self.counterparty.choices = [(cp.id, cp.name) for cp in get_counterparties()]
        self.client.choices = [(cp.id, cp.name) for cp in get_counterparties()]
        self.provider.choices = [(cp.id, cp.name) for cp in get_counterparties()]