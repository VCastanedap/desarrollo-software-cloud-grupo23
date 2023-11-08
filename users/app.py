import os
import hashlib
import psycopg2


from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'frase-secreta'


DB_HOST="" 
DB_PORT=""
DB_USERNAME=""
DB_PASSWORD=""
DB_NAME=""


def __validate_user(data):
    with psycopg2.connect(
        dbname=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                    SELECT * 
                    FROM users 
                    WHERE username = '{data.get("username")}'
                    AND email = '{data.get("email")}';
                """
            )
            result = cur.fetchone()
            return result


def __insert_user(data):
    with psycopg2.connect(
        dbname=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST
    ) as conn:
        with conn.cursor() as cur:
            result = cur.execute (
                f"""
                    INSERT INTO users (username, password, email)
                    VALUES ('{data.get("username")}', '{data.get("password")}', '{data.get("email")}');
                """
            )
            return result


@app.route("/api/auth/signup", methods=['POST'])
def signup():
    this_username = request.json.get('username')
    this_password = request.json['password']
    this_email = request.json['email']

    encrypted_password = hashlib.md5(this_password.encode('utf-8')).hexdigest()

    if not __validate_user:
        try:
            __insert_user(data={
                "username": this_username,
                "password": encrypted_password,
                "email": this_email
            })
        except Exception as e:
            return {"msg": "Bad request"}, 400
        else:
            access_token = create_access_token(identity=this_username)
            return {"msg": "Done", "access_token": access_token}, 201
    else:
        return {"msg": "User already exists"}

# @app.route("/api/auth/login", methods=["POST"])
# def login():
#     email = request.json["email"]
#     password = request.json["password"]

#     try:
#         sql_query = "SELECT * FROM usuario WHERE email = %s"
#         values = (email,)

#         cursor.execute(sql_query, values)
#         user = cursor.fetchone()

#         if user and user[2] == password:  # La columna 2 debe ser la columna de contraseña en la tabla
#             # Autenticación exitosa, generar un token JWT
#             access_token = create_access_token(identity=user[1])  # El nombre de usuario está en la columna 1
#             cursor.close()
#             conn.close()
#             return {
#                 "message": "Success login",
#                 "access_token": access_token
#             }
#         else:
#             # Autenticación fallida
#             cursor.close()
#             conn.close()
#             return {
#                 "message": "Invalid email or password"
#             }
#     except Exception as e:
#         return {
#             "message": "Error during authentication"
#         }


# @app.route("/api/auth//logout")
# def logout():
#     session.pop("username", None)
#     return {
#         "message": "Finished session"
#     }


# jwt = JWTManager(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)