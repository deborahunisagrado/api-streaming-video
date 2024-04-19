from flask import jsonify, request
from .models import *
from firebase_admin import auth


def verify_token():
    id_token = request.headers.get('Authorization')
    if not id_token:
        return jsonify({'error': 'Token não fornecido'}), 401

    try:
        decoded_token = auth.verify_id_token(id_token)
        request.uid = decoded_token['uid']
    except auth.InvalidIdTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    except auth.ExpiredIdTokenError:
        return jsonify({'error': 'Token expirado'}), 401


def init_routes(app):
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"message": "Hello, World!"})

