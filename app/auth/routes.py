from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from app.extensions import db, mail
from app.models import Movie, User, Staff, Borrow
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pandas as pd
import pickle
import os
from app.functions import *

auth_bp = Blueprint("auth", __name__)

file_path = os.path.join(os.path.dirname(__file__), "..", "recommender-models", "rec-model")
file_path = os.path.abspath(file_path)

with open(file_path, "rb") as file:
    recommendations = pickle.load(file)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=username).first()

        if user and user.check_password(password):
            session['username'] = username

            last_movie = user.lastmovie if user.lastmovie else "Jumanji"
            titles = recommendations.get(last_movie, recommendations["Jumanji"])
            links = []

            for title in titles:
                movie = Movie.query.filter_by(title=title).first()
                links.append(movie.posterpath if movie else PLACEHOLDER_POSTER)

            return render_template("main/home.html", movie_titles=titles, movie_links=links, length=len(links), user=username)

        return render_template("auth/login.html", warn="y")

    return render_template("auth/login.html", warn="n")

# Taking data from staff 
@auth_bp.route("/staff-login", methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        staff = Staff.query.filter_by(name=username).first()
        if staff and staff.check_password(password):
            orders = Borrow.query.all()
            titles = []
            deadlines = []
            usernames = []
            useremails = []

            for order in orders:
                movie = Movie.query.filter_by(id=order.movie_id).first()
                user = User.query.filter_by(id=order.user_id).first()
                titles.append(movie.title if movie else "Unknown")
                deadlines.append(order.deadline)
                usernames.append(user.name if user else "Unknown")
                useremails.append(user.email if user else "Unknown")

            return render_template(
                "staff/staff.html",
                titles=titles,
                deadline=deadlines,
                uname=usernames,
                uemail=useremails,
                length=len(usernames)
            )

        return render_template("auth/staff-login.html", warn="y")

    return render_template("auth/staff-login.html", warn="n")

# Taking data from manager login
@auth_bp.route("/manager-login", methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        password = request.form['password']
        if password.strip() == os.getenv('MANAGER_PASSWORD', '').strip():
            session['manager_logged_in'] = True
            return render_template("manager/manager.html")
        else:
            return render_template("auth/manager-login.html", warn="y")
    return render_template("auth/manager-login.html", warn="n")

def init_routes(app):
    app.register_blueprint(auth_bp)
