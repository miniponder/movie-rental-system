# Import required modules
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email=db.Column(db.String(120),unique=True, nullable= False)
    password = db.Column(db.String(128), nullable=False)
    balance=db.Column(db.Integer)
    borrows = db.relationship('Borrow', backref='user', cascade='all, delete-orphan')
    lastmovie=db.Column(db.String(100))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, name, email, password, balance=1000, lastmovie=""):
        self.name=name
        self.email=email
        self.password=generate_password_hash(password)
        self.balance=balance
        self.lastmovie=lastmovie

# Define Staff table schema
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password=generate_password_hash(password)

# Define Movie table schema
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price=db.Column(db.Integer, default=0)
    genre=db.Column(db.String(50))
    rating=db.Column(db.Float, default=0.0)
    stock=db.Column(db.Integer, default=0)
    borrows = db.relationship('Borrow', backref='movie')
    overview=db.Column(db.String(2000), default="")
    posterpath=db.Column(db.String(500), default="")
    year=db.Column(db.Integer, default=2000)

    def __init__(self, title, genre, price=0, rating=0, stock=0, overview="", posterpath="", year=2000):
        self.title=title
        self.genre=genre
        self.price = price
        self.rating =rating
        self.stock =stock
        self.overview =overview
        self.posterpath = posterpath
        self.year=year

# Define Borrow table schema
class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)

    def __init__(self, user_id, movie_id, deadline, borrow_date=None):
        self.user_id = user_id
        self.movie_id = movie_id
        self.borrow_date = borrow_date or datetime.utcnow()
        self.deadline = deadline

