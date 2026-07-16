from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, MetricsForm

# Purpose = Ideas
""" Ideas & Add-ons Here """

'''-------------Possible Add-ons-------------------------------------------------------------------'''
# JAVASCRIPT --> "search-as-you-type" functionality


'''----------------------------------------------------------------------------------'''

'''Configure Flask-Login'''
# login_manager = LoginManager()
# login_manager.init_app(app)
#
# @login_manager.user_loader
# def load_user(user_id):
#     return db.get_or_404(User, user_id)

'''Should I create DB + tables, etc. in sep file and just load them here? '''

# class Base(DeclarativeBase):
#     pass
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
# db = SQLAlchemy(model_class=Base)
# db.init_app(app)

# TABLE CONFIGS HERE

# with app.app_context():
#     db.create_all()

'''---------------Recipes-----------------------------'''



'''---------------Nutrients-----------------------------'''

# @app.route("/nutrient/<int:nutrient_id>", methods=["GET", "POST"])
# def get_nutrient(nutrient_id):
#     requested_nutrient = db.get_or_404(Nutrients, nutrient_id)
#     return render_template("nutrient.html", nutrient=requested_nutrient, current_user=current_user)

'''---------------Profile-----------------------------'''

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # # Check if user email is already present in the database.
        # result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # user = result.scalar()
        # if user:
        #     flash("This email already exists")
        #     return redirect(url_for('login'))
        # # hash_and_salted_password = generate_password_hash(
        # #     form.password.data,
        # #     method='pbkdf2:sha256',
        # #     salt_length=8
        # # )
        # new_user = User(
        #     email=form.email.data,
        #     name=form.name.data,
        #     # password=hash_and_salted_password,
        #     # password=generate_password_hash(request.form.get('password'), method='pbkdf2', salt_length=16)
        # )
        # db.session.add(new_user)
        # db.session.commit()
        # # This line will authenticate the user with Flask-Login
        # login_user(new_user)
        return redirect(url_for("metrics", current_user=current_user))
    return render_template("register.html", form=form)

@app.route('/metrics', methods=["GET", "POST"])
def metrics():
    form = MetricsForm()
    # x
    if form.validate_on_submit():
        return redirect(url_for("home", current_user=current_user))
    return render_template("register.html", form=form)

