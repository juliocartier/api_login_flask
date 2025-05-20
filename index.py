from flask import Flask, request, jsonify
from flask_cors import CORS

import pg8000
import re

from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, reqparse

app = Flask(__name__)

api = Api(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PASS = ""

@app.route('/')
def index():
    return jsonify("Bem vindo a api")

def conexao_banco():
    conn = pg8000.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=5432, database=DB_NAME)
    return conn

argumentos = reqparse.RequestParser()
argumentos.add_argument('email', type=str)
argumentos.add_argument('password', type=str)

@app.route('/criar', methods=['POST'])
def registrar():
    try:
        dados = argumentos.parse_args()
        conn = conexao_banco()
        cursor = conn.cursor()
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
    except Exception as e:
        conn.rollback()  # IMPORTANTE: desfaz transações pendentes
        print("Erro ao criar usuário:", e)
        return jsonify({"erro": "Erro ao criar usuários"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    try:
        conn = conexao_banco()
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
    except Exception as e:
        conn.rollback()  # IMPORTANTE: desfaz transações pendentes
        print("Erro ao criar usuário:", e)
        return jsonify({"erro": "Erro ao criar usuários"}), 500
    finally:
        cursor.close()
        conn.close()
        
        
@app.route("/listar_usuarios", methods=["GET"])
def get_users():
    try:
        conn = conexao_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        resultado = [dict(zip(colunas, row)) for row in users]
        return jsonify(resultado)
    except Exception as e:
        conn.rollback()  # IMPORTANTE: desfaz transações pendentes
        print("Erro ao buscar usuários:", e)
        return jsonify({"erro": "Erro ao buscar usuários"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/atualizar_usuarios/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        conn = conexao_banco()
        data = request.get_json()
        email = data.get("email")

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE USERS SET email = %s WHERE id = %s",
            (email, user_id)
        )
        conn.commit()
        return jsonify({"message": "Usuário atualizado com sucesso!"})
    except Exception as e:
        print("Erro ao atualizar usuários:", e)
        return jsonify({"erro": "Erro ao atualizar usuários"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/deletar_usuario/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = conexao_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM USERS WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "Usuário removido com sucesso!"})
    except Exception as e:
        print("Erro ao deletar usuários:", e)
        return jsonify({"erro": "Erro ao deletar usuários"}), 500
    finally:
        cursor.close()
        conn.close()



if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=5009)