import json
import random
import os
import time
import sys
import binascii
from collections import OrderedDict
from urllib.parse import urlparse
from flask import Flask, request, render_template, redirect, url_for, Response, jsonify
from flask import session as login_session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Message, Mail


app = Flask(__name__)

"""mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}"""
#app.config.update(mail_settings)
app.config.from_object(__name__)
random.seed()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50), unique=True)
    wallet_address = db.Column(db.String(50), unique=True)
    balance = db.Column(db.Integer)
    password = db.Column(db.String(80))


"""--------------------------------------------------------------------------------------------------------------------------------"""
"""-------------------------------------------------------SESSION------------------------------------------------------------------"""
"""--------------------------------------------------------------------------------------------------------------------------------"""
"""
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired(), Length(max=50)])
    age = IntegerField('Age', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])
"""

@app.route("/")
def index():
    return render_template("homepage.html", name="homepage", current_user=current_user)

@app.route("/about_us")
def about_us():
    return render_template("about_us.html", name="about_us", current_user=current_user)

@app.route("/contact_us")
def contact_us():
    return render_template("contact_us.html", name="contact_us", current_user=current_user)

@app.route("/fund_searcher")
def fund_searcher():
    return render_template("fund_searcher.html", name="fund_searcher", current_user=current_user)

@app.route("/matching")
def matching():
    return render_template("matching.html", name="matching", current_user=current_user)

@app.route("/resources")
def resources():
    return render_template("resources.html", name="resources", current_user=current_user)

@app.route("/events")
def events():
    return render_template("events.html", name="events", current_user=current_user)

"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('stockexchange'))
        return '<h2>Invalid email or password</h2>'
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    new_wallet = new_wallet_method()
    public_key = new_wallet['public_key']
    private_key = new_wallet['private_key']
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if not user:
            hashed_password = generate_password_hash(
                form.password.data, method='sha256')
            new_user = Users(email=form.email.data, password=hashed_password, name=form.name.data,
                            balance=0, wallet_address=public_key, age=form.age.data)
            send_mail(form.name.data, form.email.data,"Welcome to Mitsein {}".format(form.name.data) ,"Your private key is: {}. With this key you can make transactions. Please copy and save it in a safe place.".format(private_key))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return '<h2>Email already registered</h2>'
        # return '<h1>' + form.email.data + ' ' + form.password.data +'</h1>'

    return render_template('signup.html', form=form)

@app.route('/check/user', methods=['GET'])
def check_credentials_user():
    email = request.args.get('email')
    password = request.args.get("password")
    user = Users.query.filter_by(email=email).first()
    if user:
        if check_password_hash(user.password, password):
            return jsonify({'response': True})
        else:
            return jsonify({'response': False})
    return jsonify({'response': False})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')
"""

def send_mail(recipient_name, recipient_mail, subject, body):
    with app.app_context():
        msg = Message(subject="{}".format(subject),
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[recipient_mail], # replace with your email for testing
                      body="{}".format(body))
        mail.send(msg)

if __name__ == "__main__":
    #db.create_all()
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(debug=True, threaded=True)
