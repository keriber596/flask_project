from flask import Flask, render_template, redirect, request
from data import db_session
from flask_login import LoginManager, login_user
from forms.users import RegisterForm
from forms.login import LoginForm
from data.__all_models import User
from flask_admin import Admin


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sBPkvAZXVsSNPq1SAjNQ'
app.config['FLASK_ADMIN_SWATCH'] = 'fp2oDS32FULFk43irs'
admin = Admin(app, name='akatsuki', template_mode='bootstrap3')
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/data.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
                                   message="Такая электронная почта уже используется!")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
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


if __name__ == "__main__":
    main()