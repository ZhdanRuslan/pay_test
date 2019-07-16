from wtforms import TextField, SelectField
from wtforms.ext.i18n.form import Form
from wtforms.validators import Required


class PayForm(Form):
    amount = TextField('amount', validators=[Required()])
    currency = SelectField('currency', choices=[('978', 'EUR'), ('840', 'USD'), ('643', 'RUB')],
                           validators=[Required()])
    description = TextField('description')