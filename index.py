from flask import Flask, request, jsonify
from flask import Blueprint
from flask_cors import CORS

import psycopg2
import re

from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, reqparse

app = Flask(__name__)

api = Api(app)

CORS(app)

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "123456"

@app.route('/')
def index():
    return jsonify("Bem vindo a api")


conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

argumentos = reqparse.RequestParser()
argumentos.add_argument('email', type=str)
argumentos.add_argument('password', type=str)

@app.route('/criar', methods=['POST'])
def registrar():
    cursor = conn.cursor()

    dados = argumentos.parse_args()

    if request.method == 'POST' and 'email' in dados and 'password' in dados:
        email = dados['email']
        password = dados['password']
        _hash_password = generate_password_hash(password)
        print("Entrouuuu", email, password, _hash_password)

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            return jsonify('Essa conta já existe!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify('E-mail invalido!')
        elif not password or not email:
            return jsonify('Por favor, verifique todos os campos!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (email, password) VALUES (%s,%s)", (email, _hash_password))
            conn.commit()
            return jsonify('Criado com sucesso!')
    else:
        return jsonify('A requisição não é um método POST!')

@app.route('/login', methods=['POST'])
def login():
    cursor = conn.cursor()
    dados = argumentos.parse_args()
    if request.method == 'POST' and 'email' in dados and 'password' in dados:
        email = dados['email']
        password = dados['password']
        print(password)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        # Fetch one record and return result
        account = cursor.fetchone()
        print(account)

        if account:
            print(account)
            password_rs = account[2]
            if check_password_hash(password_rs, password):
                return jsonify('Login feito com sucesso!')
            else:
                return jsonify('Email/password Incorreto')
        else:
            return jsonify('Email/password não existe')


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=5009)