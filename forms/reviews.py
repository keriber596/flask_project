from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email


class ReviewsForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    text_reviews = StringField('Опишите свои впечатления.')
    time = StringField('Сколько часов вы ждали заказ?')
    submit = SubmitField('Отправить отзыв!')