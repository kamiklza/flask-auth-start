from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'fsdfsdfiejweimfwe'

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
            flash("You have already signed up. Please login instead.")
            return redirect(url_for('login'))
        else:
            name = request.form.get('name')
            password = request.form.get('password')
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('secrets'))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        try:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('secrets'))
        except AttributeError:
            flash("No user found")
            return redirect(url_for('login'))
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('secrets'))
            else:
                flash('Your password is incorrect')
                return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
def download():
    return send_from_directory(directory='static', filename='files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
