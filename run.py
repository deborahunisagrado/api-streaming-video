from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials
import firebase_admin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netflix.db'
db = SQLAlchemy(app)
cred = credentials.Certificate("auth-firebase.json")
firebase_admin.initialize_app(cred)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', debug=True)