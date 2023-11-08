import io

import requests
import logging

from flask import Flask, request,jsonify


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


app = Flask(__name__)

app.logger.setLevel(logging.INFO)

# cors = CORS(app)


@app.route("/api/auth/login", methods=['POST'])
def login():
    try:
        response = requests.post("http://localhost:8001/api/auth/login", json=request.json)
    except Exception as e:
        return str(e), 500
    else:
        return response.content, response.status_code


@app.route("/api/users/signup", methods=['POST'])
def signup():
    try:
        response = requests.post('http://users:8001/api/auth/signup', json=request.json)
    except Exception as e:
        return str(e), 500
    else:
        return response.content, response.status_code


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



# jwt = JWTManager(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)