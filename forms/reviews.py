from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ReviewsForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    text_reviews = StringField('Опишите свои впечатления.')
    time = StringField('Сколько часов вы ждали заказ?')
    submit = SubmitField('Отправить отзыв!')
