from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from app.extensions import db, mail
from app.models import Movie, User, Staff, Borrow
from werkzeug.security import generate_password_hash
import pandas as pd
import pickle
import os
from app.functions import *

main_bp = Blueprint("main", __name__)

PLACEHOLDER_POSTER = "https://img.lovepik.com/background/20211029/medium/lovepik-film-festival-simple-shooting-videotape-poster-background-image_605811936.jpg"


file_path = os.path.join(os.path.dirname(__file__), "..", "recommender-models", "rec-model")
file_path = os.path.abspath(file_path)

with open(file_path, "rb") as file:
    recommendations = pickle.load(file)



@main_bp.route("/")
def home():
    if Movie.query.first() is None:
        df = pd.read_csv('archive/reduced_movie_metadata.csv', low_memory=False)
        for _, row in df.iterrows():
            poster = row['poster_path']
            if not isinstance(poster, str) or poster.startswith("/"):
                poster = PLACEHOLDER_POSTER
            year = 2000
            if pd.notnull(row['release_date']):
                try:
                    year = int(str(row['release_date'])[:4])
                except ValueError:
                    pass
            movie = Movie(
                title=row['title'],
                year=year,
                genre=row['genres'],
                posterpath=poster,
                overview=row['overview'],
                stock=10,
                price=100
            )
            db.session.add(movie)
        db.session.commit()
    return render_template("auth/login.html")

@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        inp = request.form['inp']
        movie_obj = Movie.query.filter_by(title=inp).first()
        if inp not in recommendations and movie_obj is None:
            return render_template('main/blank-search.html', input=inp, movie_links=inp)
            return render_template()
        elif inp not in recommendations:
            return render_template(
                'main/search.html',
                input=inp,
                movie_links=movie_obj.posterpath,
                movie_titles=[inp],
                length=1
            )
        movie_links = [
            (Movie.query.filter_by(title=movie).first()).posterpath
            for movie in recommendations[inp]
            if Movie.query.filter_by(title=movie).first() is not None
        ]
        return render_template(
            'main/search.html',
            input=inp,
            inplink=movie_obj.posterpath,
            movie_titles=recommendations[inp],
            movie_links=movie_links,
            length=len(movie_links)
        )
    return render_template('main/search.html', input="", movie_links=[], length=0)

# Redirect to view.html 
@main_bp.route('/view/<title>', methods=['POST', 'GET'])
def view(title):
    movie = Movie.query.filter_by(title=title).first()
    if not movie:
        return render_template("404.html", message="Movie not found"), 404
    if request.method == 'POST':
        return redirect(url_for("customer.rent", title=title, warn="n"))
    return render_template(
        "main/view.html",
        title=movie.title,
        price=str(movie.price),
        genre=str(movie.genre),
        overview=movie.overview,
        posterpath=str(movie.posterpath),
        rating=str(movie.rating),
        stock=str(movie.stock)
    )

def init_routes(app):
    app.register_blueprint(main_bp)