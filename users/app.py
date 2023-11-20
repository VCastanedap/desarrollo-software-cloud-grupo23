import os
import hashlib
import psycopg2


from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "frase-secreta"
app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"

DB_HOST = "0.0.0.0"
DB_PORT = "5432"
DB_USERNAME = "postgres"
DB_PASSWORD = "bdkJ1O_BtN0=oX40"
DB_NAME = "cloud-testing"


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
            result = cur.execute(
                f"""
                    INSERT INTO users (username, password, email)
                    VALUES ('{data.get("username")}', '{data.get("password")}', '{data.get("email")}');
                """
            )
            return result


@app.route("/api/auth/signup", methods=["POST"])
def signup():
    this_username = request.json.get("username")
    this_password = request.json["password"]
    this_email = request.json["email"]

    encrypted_password = hashlib.md5(this_password.encode("utf-8")).hexdigest()

    if not __validate_user(data={"username": this_username, "email": this_email}):
        try:
            __insert_user(
                data={
                    "username": this_username,
                    "password": encrypted_password,
                    "email": this_email,
                }
            )
        except Exception as e:
            return {"msg": "Bad request"}, 400
        else:
            access_token = create_access_token(identity=this_username)
            return {"msg": "Done", "access_token": access_token}, 201
    else:
        return {"msg": "User already exists"}


@app.route("/api/auth/login", methods=["POST"])
def login():
    email = request.json["email"]
    username = request.json["username"]

    if not __validate_user(data={"username": username, "email": email}):
        return {"msg": "El usuario no existe"}, 400
    else:
        return {"token": create_access_token(identity=username)}


@app.route("/api/auth/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return {"message": "Finished session"}


jwt = JWTManager(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
