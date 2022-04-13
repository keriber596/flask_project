from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validate import validate
from config import from_email, password
from flask import Flask, render_template
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash
from data import db_session
from data.users import User
from forms.reg_user import RegisterForm
from forms.login_user import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/data.db")
    app.run()


@app.route('/')
def _():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        msg = MIMEMultipart()
        server = SMTP('smtp.gmail.com: 587')
        if validate(form.email.data):
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            message = 'Вы зарегистрировались'
            msg.attach(MIMEText(message, 'plain'))
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, form.email.data, msg.as_string())
            server.quit()
            return redirect('/login')
        else:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такого адреса не существует")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if check_password_hash(db_sess.query(User).filter(User.email.like(form.email.data)).first().hashed_password, form.password.data):
            return redirect('/')
        else:
            return render_template('login.html', title='Вход',
                                       form=form,
                                       message="Неверные данные")
    return render_template('login.html', title='Вход', form=form)


if __name__ == '__main__':
    main()
