from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from app.extensions import db, mail
from app.models import Movie, User, Staff, Borrow
from werkzeug.security import generate_password_hash
import pandas as pd
import pickle
import os
from app.functions import *

manager_bp = Blueprint("manager", __name__)

@manager_bp.route("/manager", methods=['POST', 'GET'])
def manager():
    if request.method == 'POST':
        title = request.form.get('movieName', '').strip()
        year = request.form.get('year', '2000').strip()
        genre = request.form.get('genre', '').strip()
        posterpath = request.form.get('posterpath', '').strip()
        overview = request.form.get('overview', '').strip()
        stock = request.form.get('stock', '0').strip()
        price = request.form.get('price', '0').strip()
        rating = request.form.get('rating', '0').strip()
        try:
            stock = int(stock)
        except ValueError:
            stock = 0
        try:
            price = int(price)
        except ValueError:
            price = 0
        try:
            rating = float(rating)
        except ValueError:
            rating = 0.0
        try:
            year = int(year)
        except ValueError:
            year = 2000
        add_movie(title, stock, genre, rating, year, posterpath, price, overview)
        return render_template("manager/manager.html", success="movie added successfully!")
    return render_template("manager/manager.html")
  

# Route for deleting user for manager
@manager_bp.route("/del-user", methods=['POST', 'GET'])
def del_user():
    message = None
    if request.method == 'POST':
        Username = request.form.get('username', '').strip()
        Designation = request.form.get('user_cat', '').strip()

        try:
            if Designation == 'User':
                user = User.query.filter_by(name=Username).first()
                if user:
                    if user.borrows:
                        message = f"user '{Username}' cannot be deleted — they have borrow records."
                    else:
                        db.session.delete(user)
                        db.session.commit()
                        message = f"user '{Username}' deleted successfully."
                else:
                    message = f"user '{Username}' not found."
            elif Designation == 'Staff':
                staff = Staff.query.filter_by(name=Username).first()
                if staff:
                    db.session.delete(staff)
                    db.session.commit()
                    message = f"staff '{Username}' deleted successfully."
                else:
                    message = f"staff '{Username}' not found."
            else:
                message = "invalid designation selected."
        except SQLAlchemyError as e:
            db.session.rollback()
            message = f"database error: {str(e.__cause__)}"

    return render_template("manager/del-user.html", message=message)


@manager_bp.route('/total-orders', methods=['POST', 'GET'])
def total_orders():
    orders = Borrow.query.all()
    titles = []
    ids = []
    borrow_dates = []
    deadlines = []
    uids = []
    unames = []
    for order in orders:
        movie = Movie.query.get(order.movie_id)
        user = User.query.get(order.user_id)
        titles.append(movie.title if movie else "Unknown")
        ids.append(order.id)
        borrow_dates.append(order.borrow_date)
        deadlines.append(order.deadline)
        uids.append(user.id if user else None)
        unames.append(user.name if user else "Unknown")
    length = len(titles)
    return render_template("manager/total-orders.html", id=ids, titles=titles, borrow_date=borrow_dates, deadline=deadlines, length=length, uid=uids, uname=unames)

def init_routes(app):
    app.register_blueprint(manager_bp)