from os import environ
import io

import requests
from flask import Flask, request,jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt
from flask_sqlalchemy import SQLAlchemy
from flask import send_file


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_celery:flask_celery@db:5432/flask_celery'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

db = SQLAlchemy(app)

@app.route("/")
def hello():
    print('')
    print('')
    print('')
    print(request)
    print('')
    print('')
    print('')
    print(dir(request))

    #print(requests.get('localhost:8001/'))

    # return requests.get('localhost:8001/')
    return 'Hello'


@app.route("/api/users/signup", methods=['POST'])
def signup():
    data = request.json
    destination_url = "http://localhost:8001/api/users/signup"  # URL del servicio de usuarios en localhost
    headers = {"Authorization": "Bearer your_token"}
    response = requests.post(destination_url, json=data, headers=headers)
    return response.json(), response.status_code

@app.route("/api/auth/login", methods=['POST'])
def login():
    data = request.json
    destination_url = "http://localhost:8002/api/auth/login"  # URL del servicio de autenticación en localhost
    headers = {"Authorization": "Bearer your_token"}
    response = requests.post(destination_url, json=data, headers=headers)
    return response.json(), response.status_code

@app.route("/api/auth/logout", methods=["GET"])
def logout():
    auth_service_url = "http://localhost:8001/api/auth/logout"  # Reemplaza con la URL del servicio de autenticación
    response = requests.post(auth_service_url, headers=request.headers, json=request.json)

    if response.status_code == 200:
        return 0 #redirect("/login")

    return jsonify({"error": "Error al cerrar sesión en el servicio de autenticación"}), 500


@app.route("/api/tasks/list", methods=["GET"])
def list_tasks():
    destination_url = "http://localhost:8003/api/tasks/list"  # URL del servicio de tareas en localhost
    headers = {"Authorization": "Bearer your_token"}
    response = requests.get(destination_url, headers=headers)
    return response.json(), response.status_code


@app.route("/api/tasks/retrieve/<task_id>", methods=["GET"])
def retrieve_task(task_id):
    destination_url = f"http://localhost:8003/api/tasks/retrieve/{task_id}"  # URL del servicio de tareas en localhost
    headers = {"Authorization": "Bearer your_token"}
    response = requests.get(destination_url, headers=headers)
    return response.json(), response.status_code



@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    download_service_url = f"http://localhost:9001/api/download/{filename}"  # Reemplaza con la URL del servicio de descarga
    response = requests.get(download_service_url, headers=request.headers)

    if response.status_code == 200:
        file_content = response.content
        return send_file(
            io.BytesIO(file_content),
            as_attachment=True,
            download_name=filename
        )

    return jsonify({"error": "Error al descargar el archivo desde el servicio de descarga"}), 500



jwt = JWTManager(app)