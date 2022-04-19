from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from data.users import User
from data import db_session


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
    def validate_email(self, email):
        db_sess = db_session.create_session()
        email = db_sess.query(User).filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Пользователь с данным email уже существует")