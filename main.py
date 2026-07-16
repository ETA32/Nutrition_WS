from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, MetricsForm    #???
    # ^ imports from forms.py file

import json
import csv
import os

'''-------------------------------------------'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_CONFIG_KEY']
Bootstrap5(app)

'''--------------Home-------------------------------'''

@app.route('/')
def home():
    return render_template("index.html") #current_user=current_user ;  OR logged_in=current_user.is_authenticated

@app.route('/test')
def test():
    return render_template("test.html") #current_user=current_user ;  OR logged_in=current_user.is_authenticated

@app.route('/test2')
def test2():
    return render_template("TEST popover.html")

@app.route('/test3')
def test3():
    return render_template("TEST3 popover.html")

'''--------------Recipes-------------------------------'''

@app.route('/recipes', methods=["GET", "POST"])
def recipes():
    testreciperesults = []
    # with open('RecipeSearchResultsTest.json', 'r', encoding='utf-8') as file:
    #     testreciperesults = json.load(file)
    with open('RecipeSearchResultsTestX2.csv', mode='r', newline='', encoding='utf-8') as file:
        test_reader = csv.reader(file, delimiter=',')
        for row in test_reader:
            testrecipedata = {"name": row[0], "calories": row[1], "nutrients": row[2], "restrictions": row[3], "time": row[4], "method" : row[5], "url" : row[6]}
            testreciperesults.append(testrecipedata)
    print(testreciperesults[0])
    return render_template("recipes.html", testreciperesults=testreciperesults)


'''--------------Nutrients-------------------------------'''

@app.route('/nutrients', methods=["GET", "POST"])
def nutrients():
    return render_template("nutrients.html")

'''---------------Profile-----------------------------'''

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if current_user:
        return render_template("profile.html", current_user=current_user)
    else:
        flash('Please login to view this page')
        return redirect(url_for("login"))

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect(url_for("metrics", current_user=current_user))
    return render_template("register.html", form=form)

@app.route('/metrics', methods=["GET", "POST"])
def metrics():
    form = MetricsForm()
    # x
    if form.validate_on_submit():
        return redirect(url_for("home", current_user=current_user))
    return render_template("register.html", form=form)

'''-----------------------'''

if __name__ == "__main__":
    app.run(debug=True, port=5001)