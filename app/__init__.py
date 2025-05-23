from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
import os
from app.extensions import db, mail

def create_app():
    load_dotenv()

    app = Flask(__name__, static_folder="../static")

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "..", "db.sqlite3")}'
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    )

    db.init_app(app)
    mail.init_app(app)
    from app.auth.routes import init_routes
    init_routes(app)
    from app.customer.routes import init_routes
    init_routes(app)
    from app.main.routes import init_routes
    init_routes(app)
    from app.manager.routes import init_routes
    init_routes(app)
    from app.staff.routes import init_routes
    init_routes(app)

    from app.models import Movie, User, Staff, Borrow
    with app.app_context():
        db.create_all()

    return app