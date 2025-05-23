from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from app.extensions import db, mail
from app.models import Movie, User, Staff, Borrow
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pandas as pd
import pickle
import os
from app.functions import *

customer_bp = Blueprint("customer", __name__)

file_path = os.path.join(os.path.dirname(__file__), "..", "recommender-models", "rec-model")
file_path = os.path.abspath(file_path)

with open(file_path, "rb") as file:
    recommendations = pickle.load(file)

@customer_bp.route("/create-acc", methods=['POST', 'GET'])
def create_acc():
    if request.method == 'POST':
        Username = request.form['username']
        Designation = request.form['user_cat']
        email = request.form['email']
        Password = request.form['password']
        rePassword = request.form['repassword']
        if Password != rePassword:
            return render_template("customer/create-acc.html", warn="password_mismatch")
        if User.query.filter_by(email=email).first() or Staff.query.filter_by(email=email).first():
            return render_template("customer/create-acc.html", warn="email_exists")
        if User.query.filter_by(name=Username).first() or Staff.query.filter_by(name=Username).first():
            return render_template("customer/create-acc.html", warn="user_exists")
        if Designation == 'User':
            user = User(name=Username, email=email, password=Password, lastmovie="Jumanji", balance=1000)
            db.session.add(user)
            db.session.commit()
            session['user'] = Username  # Optional
            lastmovie = "Jumanji"
            titles = recommendations.get(lastmovie, [])
            links = [(Movie.query.filter_by(title=movie).first() or Movie(title=movie, genre="", stock=0)).posterpath for movie in titles]
            return render_template("main/home.html", movie_titles=titles, movie_links=links, length=len(links), user=Username)
        elif Designation == 'Staff':
            staff = Staff(name=Username, email=email, password=Password)
            db.session.add(staff)
            db.session.commit()
            session['staff'] = Username
            orders = Borrow.query.all()
            titles = [Movie.query.get(order.movie_id).title for order in orders]
            deadlines = [order.deadline for order in orders]
            unames = [User.query.get(order.user_id).name for order in orders]
            uemails = [User.query.get(order.user_id).email for order in orders]
            return render_template('staff/staff.html', titles=titles, deadline=deadlines, uname=unames, uemail=uemails, length=len(unames))
    return render_template("customer/create-acc.html", warn="n")

@customer_bp.route("/customer", methods=['POST', 'GET'])
def customer():
    if 'username' not in session:
        return redirect(url_for('login.html'))
    
    username = session['username']
    user = User.query.filter_by(name=username).first()
    if not user:
        return "user not found", 404
    
    rentals = Borrow.query.filter_by(user_id=user.id).all()
    titles = [Movie.query.get(rental.movie_id).title for rental in rentals]
    ids = [rental.id for rental in rentals]
    borrow_dates = [rental.borrow_date for rental in rentals]
    deadlines = [rental.deadline for rental in rentals]
    length = len(titles)
    balance = user.balance
    
    if request.method == "POST":
        rating = float(request.form['rating'])
        titlesel = request.form['titlesel']
        movie = Movie.query.filter_by(title=titlesel).first()
        if movie:
            movie.rating += rating
            db.session.add(movie)
            db.session.commit()
        else:
            return "movie not found", 404
            
    return render_template("customer/customer.html", id=ids, balance=balance, titles=titles, 
                          borrow_date=borrow_dates, deadline=deadlines, length=length, 
                          user=username)

@customer_bp.route('/rent/<title>', methods=['POST', 'GET'])
def rent(title):
    movie = Movie.query.filter_by(title=title).first()
    if not movie:
        return render_template("404.html", message="Movie not found"), 404
    if request.method == 'POST':
        Username = request.form['username']
        user = User.query.filter_by(name=Username).first()
        if not user:
            return render_template("customer/rent.html", title=title, price=movie.price, genre=movie.genre, overview=movie.overview,
                                   posterpath=movie.posterpath, rating=movie.rating, stock=movie.stock, warn="yuser")
        if movie.stock == 0:
            return render_template("customer/ent.html", title=title, price=movie.price, genre=movie.genre, overview=movie.overview,
                                   posterpath=movie.posterpath, rating=movie.rating, stock=movie.stock, warn="ystock")
        if user.balance < movie.price:
            return render_template("customer/rent.html", title=title, price=movie.price, genre=movie.genre, overview=movie.overview,
                                   posterpath=movie.posterpath, rating=movie.rating, stock=movie.stock, warn="ybalance")
        rent_movie(user.id, movie.id)
        rentals = Borrow.query.filter_by(user_id=user.id).all()
        titles = [Movie.query.get(r.movie_id).title for r in rentals]
        ids = [r.id for r in rentals]
        borrow_dates = [r.borrow_date for r in rentals]
        deadlines = [r.deadline for r in rentals]
        length = len(titles)
        balance = user.balance
        return render_template("customer/customer.html", id=ids, balance=balance, titles=titles, borrow_date=borrow_dates,
                               deadline=deadlines, length=length, user=Username)
    return render_template("customer/rent.html", title=title, price=movie.price, genre=movie.genre, overview=movie.overview,
                           posterpath=movie.posterpath, rating=movie.rating, stock=movie.stock, warn="n")

def init_routes(app):
    app.register_blueprint(customer_bp)
