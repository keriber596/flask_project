from flask import Flask, render_template, url_for, redirect, request
from flask_login import LoginManager, login_user, logout_user
from flask_bootstrap import Bootstrap

from data import db_session
from data.users import User
from data.reviews import Review
from forms.reg_user import RegisterForm
from forms.login_user import LoginForm
from forms.reviews import ReviewsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
boostrap = Bootstrap(app)


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
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
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
        return redirect(url_for("login"))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("index"))
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


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


@app.route("/logout")
def logout():
    logout_user()
    return redirect("index")


@app.route("/menu")
def menu():
    return render_template("menu.html", title="МЕНЮ")


if __name__ == '__main__':
    main()
