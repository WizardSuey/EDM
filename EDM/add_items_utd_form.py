from wtforms import IntegerField, StringField, DecimalField, SubmitField, Form
from wtforms.validators import DataRequired, Length, NumberRange

class UtdDocumentItemsForm(Form):
    utd_document_id = IntegerField('UTD Document ID', validators=[DataRequired()])
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=255)])
    product_quantity = IntegerField('Product Quantity', validators=[DataRequired(), NumberRange(min=0)])
    product_price = DecimalField('Product Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    product_sum = DecimalField('Product Sum', validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UtdDocumentItemsForm, self).__init__(*args, **kwargs)