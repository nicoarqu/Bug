import json
import random
import os
import time
import sys
import binascii
import nltk
import random
nltk.download('punkt')
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from flask import Flask, request, render_template, jsonify
from flask import session 
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail
from flask_babel import Babel
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
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
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español'
}
app.config['RECAPTCHA_USE_SSL']= False
app.config['RECAPTCHA_PUBLIC_KEY']=os.environ.get("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY']=os.environ.get("RECAPTCHA_PRIVATE_KEY")
app.config['RECAPTCHA_OPTIONS']= {'theme':'black'}

Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

from models import Users, Notifications, News, Grants
Base = declarative_base()
Base.query = db_session.query_property()


"""--------------------------------------------------------------------------------------------------------------------------------"""
"""-------------------------------------------------------SESSION------------------------------------------------------------------"""
"""--------------------------------------------------------------------------------------------------------------------------------"""

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    password = PasswordField('Clave', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Recuérdame')

class RegisterForm(FlaskForm):
    name = StringField('Nombre', validators=[InputRequired(), Length(max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    nationality = StringField('Nacionalidad', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Clave', validators=[
                             InputRequired(), Length(min=8, max=80)])

class ContactForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    text = StringField('Mensaje', validators=[
                             InputRequired()],widget=TextArea())

class SearchForm(FlaskForm):
    text = StringField('', validators=[InputRequired(), Length(max=100)])

@app.route("/")
def index():
    return render_template("homepage.html", name="homepage", session=session)

@app.route("/about_us")
def about_us():
    return render_template("about_us.html", name="about_us", current_user=current_user)

@app.route("/contact_us", methods=['GET', 'POST'])
def contact_us():
    form = ContactForm()
    email = form.email.data
    text = form.text.data
    num_notifications = 0
    return render_template("contact_us.html", name="contact_us", current_user=current_user, form=form)


def get_important_words(description):
    text_tokens = word_tokenize(description)
    tokens_without_sw = [word.lower() for word in text_tokens if not word in stopwords.words()]
    return tokens_without_sw

def get_search_matches(text, new_grants_list):
    clean_text = get_important_words(text)
    list_posible_grants = list()
    try:
        if len(new_grants_list) >=30:
            for grant in new_grants_list[:30]:
                dict_posible_grant = {"titulo": grant["titulo"], "num": 0, "pubDate": grant["pubDate"], "summary": grant["summary"], "link": grant["link"]}
                important_words = get_important_words(str(grant["titulo"].lower()+" "+str(grant["summary"]).lower()))
                for word in clean_text:
                    if word in important_words:
                        dict_posible_grant['num'] += 1
                        continue
                if dict_posible_grant["num"] > 0:
                    list_posible_grants.append(dict_posible_grant)
        return list_posible_grants
    except:
        return list_posible_grants

@app.route("/fund_searcher", methods=['GET', 'POST'])
def fund_searcher():
    form = SearchForm()
    top_list = list()
    grants = Grants.query.all()
    new_grants_list = []
    for grant in grants:
        new_grants_list.append({"titulo": grant.title, "link":grant.link ,"summary":grant.description, "pubDate":grant.datetime})
    if form.validate_on_submit(): 
        text = form.text.data
        list_posible_grants = get_search_matches(text, new_grants_list)
        if len(list_posible_grants) > 0:
            top_list = sorted(list_posible_grants, key=lambda k: k['num'], reverse=True)
        return render_template("fund_searcher.html", name="fund_searcher", current_user=current_user, new_grants_list=top_list, form=form)
    return render_template("fund_searcher.html", name="fund_searcher", current_user=current_user, new_grants_list=new_grants_list, form=form)

@app.route("/matching", methods=['GET', 'POST'])
def matching():
    form = ContactForm()
    email = form.email.data
    text = form.text.data
    content_html= "<br><p>{}</p><br><p>{}</p>".format(text, email)
    if form.validate_on_submit():
        #send_mail(app.config.get("MAIL_USERNAME"), "Cliente quiere contactarse", content_html)
        pass
    return render_template("matching.html", name="matching", current_user=current_user, form=form)

@app.route("/resources")
def resources():
    return render_template("resources.html", name="resources", current_user=current_user)

@app.route("/news")
def news():
    new_news_list = list()
    news = News.query.all()
    for n in news:
        new_news_list.append({"titulo": n.title, "link":n.link ,"summary":n.description, "pubDate":n.datetime})
    new_news_list.sort(key=lambda item:item['pubDate'], reverse=True)
    return render_template("events.html", name="events", current_user=current_user, new_news_list=new_news_list)

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
            #send_mail(form.email.data,"Bienvenido/a a BUG" ,"Te damos la bienvenida a BUG Creative Industry Network {}".format(form.name.data))
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
    user = Users.query.filter_by(email=current_user.email).first()
    logout_user()
    session['logged_in'] = False
    return render_template("homepage.html", name="homepage", session=session)


@app.route('/profile')
@login_required
def profile():
    return render_template('user_profile.html')


if __name__ == "__main__":
    db.create_all()
    Base.metadata.create_all(bind=engine)
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(debug=True, threaded=True)
