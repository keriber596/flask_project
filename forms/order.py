from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    address = StringField("Ваш адрес", validators=[DataRequired()])
    payment = SelectField('Способ оплаты', choices=[('card', 'Карта'), ('cash', 'Наличные')])
    submit = SubmitField("Подтвердить")
