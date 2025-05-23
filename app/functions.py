from datetime import datetime, timedelta
from app.models import User, Movie, Borrow, db
from flask import flash
from fpdf import FPDF
import os
from sqlalchemy.exc import SQLAlchemyError

# Utility function to implement necessary changes in the database when a movie is rented.
def rent_movie(user_id, movie_id):
    try:
        user_obj = User.query.filter_by(id=user_id).first()  # sure to exist
        movie_obj = Movie.query.filter_by(id=movie_id).first()

        if movie_obj is None:
            raise ValueError("movie not found ☹️")

        if user_obj.balance < movie_obj.price:
            raise ValueError("insufficient balance. please add funds to your account to rent this film.")
        if movie_obj.stock < 1:
            raise ValueError("out of stock 😔")

        my_order = Borrow(
            user_id=user_obj.id,
            movie_id=movie_id,
            borrow_date=datetime.utcnow(),
            deadline=datetime.utcnow() + timedelta(days=30)
        )
        movie_obj.stock -= 1
        user_obj.balance -= movie_obj.price
        user_obj.lastmovie = movie_obj.title
        db.session.add(my_order)
        db.session.commit()
        flash('congratulations! movie rented successfully! 🤩')
        generate_receipt(my_order.id)

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        flash(str(e))

# Utility function to generate a PDF receipt of the order of a user.
def generate_receipt(order_id):
    try:
        order_obj = Borrow.query.filter_by(id=order_id).first()
        movie_obj = Movie.query.filter_by(id=order_obj.movie_id).first()
        user_obj = User.query.filter_by(id=order_obj.user_id).first()

        if not order_obj or not movie_obj or not user_obj:
            raise KeyError("order not found! ❌")

        receipt = FPDF()
        receipt.add_page()
        receipt.set_font('Courier', 'B', 16)
        receipt.cell(200, 10, 'movie rentals', 0, 1, 'C')
        receipt.cell(200, 10, 'receipt', 0, 1, 'C')

        receipt.set_font('Courier', '', 12)
        receipt.cell(200, 10, f"order id: {order_obj.id}", 0, 1, 'L')
        receipt.cell(200, 10, f"customer id: {user_obj.id}", ln=1, align="L")
        receipt.cell(200, 10, f"customer name: {user_obj.name}", ln=1, align="L")
        receipt.cell(200, 10, f"movie id: {movie_obj.id}", ln=1, align="L")
        receipt.cell(200, 10, f"movie name: {movie_obj.title}", ln=1, align="L")
        receipt.cell(200, 10, f"movie genre: {movie_obj.genre}", ln=1, align="L")
        receipt.cell(200, 10, f"date: {order_obj.borrow_date}", ln=1, align="L")
        receipt.set_font('Courier', 'B', 16)
        receipt.cell(200, 10, f"total price: {movie_obj.price}", ln=1, align="C")

        base_dir = os.path.abspath(os.path.dirname(__file__))
        receipt_dir = os.path.join(base_dir, 'Receipts')
        os.makedirs(receipt_dir, exist_ok=True)
        receipt_path = os.path.join(receipt_dir, f"receipt{order_obj.id}.pdf")
        receipt.output(receipt_path)
        flash("receipt generated successfully and downloaded 👍")

    except KeyError as e:
        flash(str(e))

# Utility function to return an outstanding order.
def return_movie(order_id, rating, people):
    try:
        order_obj = Borrow.query.filter_by(id=order_id).first()
        if not order_obj:
            raise ValueError("order not found! ❌")

        movie_obj = Movie.query.filter_by(id=order_obj.movie_id).first()
        if not movie_obj:
            raise ValueError("movie not found! ❌")

        movie_obj.rating = ((movie_obj.rating * (people - 1)) + rating) / people
        movie_obj.stock += 1
        db.session.commit()
        flash("movie returned successfully! 🥳")

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        flash(str(e))

# Utility function to return a list of all orders that the user has created on the VRS.
def view_orders(user_id):
    try:
        user_obj = User.query.filter_by(id=user_id).first()
        if user_obj is None:
            raise KeyError("user not found! ❌")
        return Borrow.query.filter_by(user_id=user_id).all()
    except KeyError as e:
        flash(str(e))
    return None

# Add a movie to the database
def add_movie(title, stock, genre="", rating=0, year=0,
              img_path="https://img.lovepik.com/background/20211029/medium/lovepik-film-festival-simple-shooting-videotape-poster-background-image_605811936.jpg",
              price=0, overview=""):
    try:
        movie_obj = Movie.query.filter_by(title=title).first()
        if movie_obj:
            movie_obj.stock += stock
            if price != 0:
                movie_obj.price = price
        else:
            movie_obj = Movie(title=title, genre=genre, rating=rating, price=price,
                              stock=stock, year=year, posterpath=img_path, overview=overview)
            db.session.add(movie_obj)
        db.session.commit()
        flash("movie added successfully! 🤩")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("error while adding movie. ❗️")
