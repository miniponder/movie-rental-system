from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from app.extensions import db, mail
from app.models import Movie, User, Staff, Borrow
from werkzeug.security import generate_password_hash
import pandas as pd
import pickle
import os
from app.functions import *

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff", methods=['POST', 'GET'])
def staff():
    orders = Borrow.query.all()
    titles = [(Movie.query.get(order.movie_id)).title for order in orders]
    deadlines = [order.deadline for order in orders]
    unames = [(User.query.get(order.user_id)).name for order in orders]
    uemails = [(User.query.get(order.user_id)).email for order in orders]
    length = len(unames)
    return render_template("staff/staff.html", titles=titles, deadline=deadlines, uname=unames, uemail=uemails, length=length)

@staff_bp.route('/send-mail', methods=['POST', 'GET'])
def sendmail():
    orders = Borrow.query.all()
    titles = [Movie.query.get(order.movie_id).title for order in orders]
    deadline = [order.deadline for order in orders]
    uname = [User.query.get(order.user_id).name for order in orders]
    uemail = [User.query.get(order.user_id).email for order in orders]
    length = len(uname)
    if request.method == 'POST':
        temp = request.form['recipients']
        message = request.form['message']
        all_users_flag = request.form.get('allusers')
        user_names = [name.strip() for name in temp.split(',') if name.strip()]
        if all_users_flag == "User":
            emails = [user.email for user in User.query.all()]
            mail.send_message('movie rental system', sender=current_app.config['MAIL_USERNAME'], recipients=emails, body=message)
        else:
            emails = []
            for username in user_names:
                user = User.query.filter_by(name=username).first()
                if user:
                    emails.append(user.email)
            if emails:
                mail.send_message('Video Rental System', sender=current_app.config['MAIL_USERNAME'], recipients=emails, body=message)
        return render_template('staff/staff.html', titles=titles, deadline=deadline, uname=uname, uemail=uemail, length=length)
    return render_template('staff/staff.html', titles=titles, deadline=deadline, uname=uname, uemail=uemail, length=length)

def init_routes(app):
    app.register_blueprint(staff_bp)
    