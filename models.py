from flask_app import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON


class Users(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Notifications(db.Model):
    __tablename__ = 'Notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    read = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, date, description, read):
        self.user_id = user_id
        self.date = date
        self.description = description
        self.read = read

    def __repr__(self):
        return '<id {}>'.format(self.id)

class News(db.Model):
    __tablename__ = 'News'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    link = db.Column(db.String(1000))
    datetime = db.Column(db.String(50))

    def __init__(self, title, description, link, datetime):
        self.title = title
        self.description = description
        self.link = link
        self.datetime = datetime

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Grants(db.Model):
    __tablename__ = 'Grants'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    link = db.Column(db.String(1000))
    datetime = db.Column(db.String(50))

    def __init__(self, title, description, link, datetime):
        self.title = title
        self.description = description
        self.link = link
        self.datetime = datetime

    def __repr__(self):
        return '<id {}>'.format(self.id)