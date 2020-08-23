import json
import random
import os
import time
import sys
import binascii
from collections import OrderedDict
from urllib.parse import urlparse
from flask import Flask, request, render_template, redirect, url_for, Response, jsonify
from flask import session 
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
from flask_babel import Babel, gettext
from apscheduler.schedulers.background import BackgroundScheduler
import load_global
import re


app = Flask(__name__)
babel = Babel(app)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}
app.config.update(mail_settings)
app.config.from_object(__name__)
random.seed()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bug_database.db'
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español'
}

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
    nationality = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))



"""--------------------------------------------------------------------------------------------------------------------------------"""
"""-------------------------------------------------------SESSION------------------------------------------------------------------"""
"""--------------------------------------------------------------------------------------------------------------------------------"""

class SearchForm(FlaskForm):
    text = StringField('Search', validators=[InputRequired(), Length(max=100)])

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
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    nationality = StringField('Nationality', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    text = StringField('text', validators=[
                             InputRequired()])

@app.route("/")
def index():
    form = SearchForm()
    return render_template("homepage.html", name="homepage", session=session, form=form)

@app.route("/about_us")
def about_us():
    return render_template("about_us.html", name="about_us", current_user=current_user)

@app.route("/contact_us")
def contact_us():
    return render_template("contact_us.html", name="contact_us", current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                session['logged_in'] = True
                login_user(user, remember=form.remember.data)
                return render_template("homepage.html", name="homepage", session=session)
        return '<h2>Invalid email or password</h2>'
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if not user:
            hashed_password = generate_password_hash(
                form.password.data, method='sha256')
            new_user = Users(email=form.email.data, password=hashed_password, name=form.name.data, nationality=form.nationality.data)
            send_mail(form.name.data, form.email.data,"Welcome to BUG" ,"Welcome to the BUG Creative Industry Network {}".format(form.name.data))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            session['logged_in'] = True
            return render_template("homepage.html", name="homepage", session=session)
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
    form = SearchForm()
    user = Users.query.filter_by(email=current_user.email).first()
    logout_user()
    session['logged_in'] = False
    return render_template("homepage.html", name="homepage", session=session, form=form)

@app.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')

def send_mail(recipient_name, recipient_mail, subject, body):
    with app.app_context():
        msg = Message(subject="{}".format(subject),
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[recipient_mail], # replace with your email for testing
                      body="{}".format(body))
        mail.send(msg)


if __name__ == "__main__":
    db.create_all()
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(debug=True, threaded=True)
