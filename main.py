from flask import Flask, render_template, url_for, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_bootstrap import Bootstrap
from funs import pcheck
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validate import validate
import csv
from data import db_session
from data.users import User
from data.reviews import Review
from forms.reg_user import RegisterForm
from forms.login_user import LoginForm

from forms.reviews import ReviewsForm
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
from_email = 'wqisup@gmail.com'
password = 'Yq5-4DY-eJw-CMq'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/data.db")
    app.run()


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    reviews_page = db_sess.query(Review)
    return render_template('index.html', reviews=reviews_page)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                                message="Неправильный логин или пароль",
                                form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/index")


@app.route('/map', methods=['GET', 'POST'])
def map():

    return render_template('map.html')


@app.route("/menu")
def menu():
    menu_list=[]
    with open('static/csv/food_items.csv', encoding='utf8') as csvfile:
        reader= csv.reader(csvfile, delimiter='-')
        for i, j in enumerate(reader):
            if i==0:

                continue
            else:
                menu_list.append(j)
    return render_template("menu.html", title="МЕНЮ", menu_list=menu_list)

@app.route("/basket")
def add_to_basket():
    pass

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    form = ReviewsForm()
    if request.method == "POST":
        db_sess = db_session.create_session()
        review = Review(
            name=form.name.data,
            text=form.text_reviews.data,
            time=form.time.data
        )
        db_sess.add(review)
        db_sess.commit()
        return redirect(url_for("index"))
    return render_template('reviews.html', form=form)


@app.route('/reviews_page', methods=['GET'])
def reviews_page():
    db_sess = db_session.create_session()
    reviews_page = db_sess.query(Review)
    return render_template("reviews_page.html", reviews=reviews_page)

if __name__ == '__main__':
    main()
