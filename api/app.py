import os
import stat

from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt

from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from flask import jsonify
from flask import send_file

app = Flask(__name__)
app.secret_key = "your_secret_key"

jwt = JWTManager(app)

@app.route('upload/<filename>')
def upload_file():
    from broker.tasks import tasks



    tasks('nombre_archivo')
    return response()

@app.route("/download/<filename>")
def download_file(filename):
    try:
        upload_folder = app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, filename)

        # Logeamos los permisos del archivo
        file_stat = os.stat(file_path)
        permissions = stat.filemode(file_stat.st_mode)
        app.logger.info(f"Permissions for {file_path}: {permissions}")

        app.logger.info(
            f'Contenido del directorio "uploads" antes de la descarga: {os.listdir(upload_folder)}'
        )

        # Utilizando send_file con ruta absoluta
        absolute_path = os.path.abspath(file_path)
        return send_file(absolute_path, as_attachment=True)
    except FileNotFoundError:
        app.logger.info(
            f'Contenido del directorio "uploads" después de no encontrar el archivo: {os.listdir(upload_folder)}'
        )
        return "Archivo no encontrado", 404





app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
