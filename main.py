import csv
from data import db_session
from data.reviews import Review
from data.users import User
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_validate import validate
from flask import Flask, render_template, url_for, redirect, request, make_response
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from forms.login_user import LoginForm
from forms.order import OrderForm
from forms.reg_user import RegisterForm
from forms.reviews import ReviewsForm

from funs import pcheck
from smtplib import SMTP

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


def read_csv(content):
    with open("static/csv/food_items.csv", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter="-")
        res = []
        for i in reader:
            if i[0] in content:
                for j in range(content.count(i[0])):
                    res.append(i[2])
        prices = [int(i.rstrip("₽")) for i in res]
        s = sum(prices)
    return s, prices, len(content)


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    reviews = db_sess.query(Review)
    reviews = reviews[-3:]
    return render_template('index.html', reviews=reviews)


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

            error = pcheck(form.password.data)
            if not error:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message=error)
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


@app.route("/menu")
def menu():
    menu_list = []
    with open('static/csv/food_items.csv', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter='-')
        for i, j in enumerate(reader):
            if i == 0:
                continue
            else:
                menu_list.append(j)
    return render_template("menu.html", title="МЕНЮ", menu_list=menu_list)


@app.route("/basket")
@login_required
def basket():
    content = request.cookies.get(current_user.email)
    if content is None:
        clear_basket()
        prices, total, length = 0, 0, 0
    else:
        content = content.split("-")
        total, prices, length = read_csv(content)
    return render_template("basket.html", content=content, total=total, len=length)


@app.route("/add/<item>")
@login_required
def add_to_basket(item):
    content = request.cookies.get(current_user.email)
    if content != "" and content is not None:
        content = content.split("-")
        content.append(item)
    else:
        content = []
        content.append(item)
    total, prices, length = read_csv(content)
    resp = make_response(render_template("basket.html", content=content, prices=prices, total=total, len=len(content)))
    resp.set_cookie(current_user.email, "-".join(content), max_age=60 * 60 * 48)
    return resp


@app.route("/clear_basket")
@login_required
def clear_basket():
    resp = make_response(render_template("basket.html", content=[""]))
    resp.set_cookie(current_user.email, "")
    return resp


@app.route('/review_form', methods=['GET', 'POST'])
def review_form():
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
    return render_template('review_form.html', form=form)


@app.route('/make_order')
@login_required
def order():
    content = request.cookies.get(current_user.email)
    if content != "":
        total, rest, rest1 = read_csv(content)
        form = OrderForm()
        msg = None
        resp = make_response(render_template("order.html", form=form, total=total, msg=msg))
        resp.set_cookie(current_user.email, "")
        return resp
    return redirect(url_for('msg'))


@app.route('/msg')
@login_required
def msg():
    return render_template('msg.html')


@app.route('/all_reviews')
def all_reviews():
    db_sess = db_session.create_session()
    content = db_sess.query(Review)
    return render_template('all_reviews.html', content=content)


if __name__ == '__main__':
    main()
