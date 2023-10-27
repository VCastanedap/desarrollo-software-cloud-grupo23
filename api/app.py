import os
import stat

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt

from flask import send_file

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_celery:flask_celery@db:5432/flask_celery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)

db = SQLAlchemy()

app_context = app.app_context()
app_context.push()

db.init_app(app)

upload_folder = app.config["UPLOAD_FOLDER"]


@app.route('/api/upload/<filename>', methods=['POST'])
def upload_file():
    # try create new task with the file 
    pass

@app.route("/api/download/<filename>")
def download_file(filename):
    try:
        file_path = os.path.join(upload_folder, filename)
        
        file_stat = os.stat(file_path)
        permissions = stat.filemode(file_stat.st_mode)
        app.logger.info(f"Permissions for {file_path}: {permissions}")

        app.logger.info(
            f'Uploads before download: {os.listdir(upload_folder)}'
        )

        absolute_path = os.path.abspath(file_path)
        return send_file(absolute_path, as_attachment=True)
    except FileNotFoundError:
        app.logger.info(
            f'Contenido del directorio "uploads" después de no encontrar el archivo: {os.listdir(upload_folder)}'
        )
        return "Archivo no encontrado", 404



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
