# from run import app
import json
import requests
import os
from flask import Flask, request, jsonify
from firebase_admin import auth
from dotenv import load_dotenv


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