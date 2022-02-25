import bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import null

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), nullable=False, unique=True, primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(150), nullable=False,unique=True)
    phone = db.Column(db.Numeric, nullable=False, unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))  


    @classmethod
    def register(cls,username, password, email, phone, first_name, last_name):
        """Register a user, hashing their password."""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(username=username,password=hashed_utf8,email=email, phone=phone, first_name=first_name,last_name=last_name) 

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user=User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False    

class Watchlist(db.Model):
    __tablename__ = "watchlists"

    id= db.Column(db.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    username = username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
    symbol = db.Column(db.Text, nullable=False)

    users = db.relationship('User', backref="watchlists")
