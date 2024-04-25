from flask import Flask, request, jsonify
from firebase_admin import auth
from dotenv import load_dotenv
import json
import requests
import os
from datetime import date


app = Flask(__name__)
from app.models.models import User, Titulos, Historico, Lista_reproducao, Lista_reproducao_titulos, Generos

load_dotenv()
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
    @app.before_request
    def before_request_func():
        if request.endpoint not in ['login', 'signup']:
            return verify_token()

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        email = data['email']
        password = data['password']
        name = data['name']

        try:
            user_record = auth.create_user(email=email, password=password)
            firebase_uid = user_record.uid
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        try:
            new_user = User(email=email, name=name, data_criacao=str(date.today()))
            new_user.save()
        except Exception as e:
            auth.delete_user(firebase_uid)
            return jsonify({"error": str(e)}), 400

        return jsonify({"message": "User created successfully", "firebase_uid": firebase_uid}), 201


    @app.route('/login', methods=['POST'])
    def login():
        email = request.json['email']
        password = request.json['password']

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('FIREBASE_API_KEY')}"

        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            return jsonify({'error': 'Credenciais inválidas'}), 401

        json_response = response.json()
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': json_response['idToken'],
            'refreshToken': json_response['refreshToken']
        }), 200


    @app.route('/usuarios/<int:user_id>', methods=['GET'])
    def get_usuario(user_id):
        usuario = User.query.get(user_id)
        if usuario:
            usuario_info = {
                "id": usuario.id,
                "name": usuario.name,
                "email": usuario.email,
                "data_criacao": usuario.data_criacao
            }
            return jsonify(usuario_info), 200
        else:
            return jsonify({"message": "Usuário não encontrado"}), 404

    @app.route('/titulos', methods=['POST'])
    def criar_titulo():
        data = request.get_json()
        novo_titulo = Titulos(
            titulo=data['titulo'],
            sinopse=data['sinopse'],
            elenco=data['elenco'],
            diretor=data['diretor'],
            ano_lancamento=data['ano_lancamento'],
            ava_media=data['ava_media'],
            data_criacao=datetime.now()
        )
        novo_titulo.save()
        return jsonify({"message": "Título criado com sucesso"}), 201

    @app.route('/titulos', methods=['GET'])
    def listar_titulos():
        titulos = Titulos.query.all()
        lista_titulos = [{
            "id": titulo.id,
            "titulo": titulo.titulo,
            "sinopse": titulo.sinopse,
            "elenco": titulo.elenco,
            "diretor": titulo.diretor,
            "ano_lancamento": titulo.ano_lancamento,
            "ava_media": titulo.ava_media
        } for titulo in titulos]
        return jsonify(lista_titulos), 200

    @app.route('/historico', methods=['POST'])
    def registrar_historico():
        data = request.get_json()
        novo_historico = Historico(
            id_usuario=data['id_usuario'],
            id_titulo=data['id_titulo'],
            data_criacao=datetime.now()
        )
        novo_historico.save()
        return jsonify({"message": "Histórico registrado com sucesso"}), 201

    @app.route('/listas', methods=['POST'])
    def criar_lista_reproducao():
        data = request.get_json()
        nova_lista = Lista_reproducao(
            id_usuario=data['id_usuario'],
            nome=data['nome'],
            descricao=data['descricao']
        )
        nova_lista.save()
        return jsonify({"message": "Lista de reprodução criada com sucesso"}), 201

    @app.route('/listas/<int:id_lista>/titulos', methods=['POST'])
    def adicionar_titulo_lista(id_lista):
        data = request.get_json()
        nova_assoc = Lista_reproducao_titulos(
            id_lista=id_lista,
            id_titulo=data['id_titulo']
        )
        nova_assoc.save()
        return jsonify({"message": "Título adicionado à lista com sucesso"}), 201

    @app.route('/generos', methods=['POST'])
    def criar_genero():
        data = request.get_json()
        novo_genero = Generos(nome=data['nome'])
        novo_genero.save()
        return jsonify({"message": "Gênero criado com sucesso"}), 201

