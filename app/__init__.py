from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials
import firebase_admin

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netflix.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cred = credentials.Certificate("auth-firebase.json")
    firebase_admin.initialize_app(cred)

    db.init_app(app)
    
    from .models import User, Titulos, Historico, Lista_reproducao, Lista_reproducao_titulos, Generos

    with app.app_context():
        db.create_all()

    from .routes import init_routes
    init_routes(app)

    return app
