import io

import requests
import logging

from flask import Flask, request, jsonify, redirect


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


app = Flask(__name__)

app.logger.setLevel(logging.INFO)


@app.route("/api/users/login", methods=["POST"])
def login():
    try:
        response = requests.post("http://users:8001/api/auth/login", json=request.json)
    except Exception as e:
        return str(e), 500
    else:
        return response.content, response.status_code


@app.route("/api/users/signup", methods=["POST"])
def signup():
    try:
        response = requests.post("http://users:8001/api/auth/signup", json=request.json)
    except Exception as e:
        return str(e), 500
    else:
        return response.content, response.status_code


@app.route("/api/users/logout", methods=["GET"])
def logout():
    try:
        requests.get("http://users:8001/api/auth/logout")
    except Exception as e:
        return str(e), 500
    else:
        return {"message": "done"}


def __validate_token(token):
    if token is None or not token.startswith("Bearer "):
        return False
    else:
        return True


@app.route("/api/tasks/list", methods=["GET"])
def list_tasks():
    if __validate_token(token=request.headers.get("Authorization")):
        response = requests.get("http://tasks:9001/api/tasks/list")
        return response.content, response.status_code
    else:
        return jsonify({"error": "Authorization header is missing or invalid"}), 401


@app.route("/api/tasks/retrieve/<task_id>", methods=["GET"])
def retrieve_task(task_id):
    if __validate_token(token=request.headers.get("Authorization")):
        response = requests.get(f"http://tasks:9001/api/tasks/retrieve/{task_id}")
        return response.content, response.status_code
    else:
        return jsonify({"error": "Authorization header is missing or invalid"}), 401


@app.route("/api/tasks/create", methods=["POST"])
def create_task():
    if __validate_token(token=request.headers.get("Authorization")):
        response = requests.post(
            f"http://tasks:9001/api/tasks/create", json=request.json
        )
        return response.content, response.status_code
    else:
        return jsonify({"error": "Authorization header is missing or invalid"}), 401


@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    download_service_url = f"http://localhost:9001/api/download/{filename}"  # Reemplaza con la URL del servicio de descarga
    response = requests.get(download_service_url, headers=request.headers)

    if response.status_code == 200:
        file_content = response.content
        return send_file(
            io.BytesIO(file_content), as_attachment=True, download_name=filename
        )

    return (
        jsonify(
            {"error": "Error al descargar el archivo desde el servicio de descarga"}
        ),
        500,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
