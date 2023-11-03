from datetime import datetime

from os import environ

from flask import Flask, request, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

# import psycopg2


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_celery:flask_celery@db:5432/flask_celery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)

db = SQLAlchemy(app)

cors = CORS(app)


class FileConversionTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('file_conversion_tasks', lazy=True))
    original_filename = db.Column(db.String(255), nullable=False)
    converted_filename = db.Column(db.String(255))
    original_filepath = db.Column(db.String(255), nullable=False)
    converted_filepath = db.Column(db.String(255))
    conversion_format = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='unavailable')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/tasks")
def hello():
    return jsonify({"message": "Hello to Tasks"})

"""
connection = psycopg2.connect(
    host="postgres",
    port=5432,
    user="flask_celery",
    password="flask_celery",
    database="flask_celery"
)
"""

"""

def __extract_tasks(tasks):
    return [
        {
            'id': record[0],
            'original_filename': record[3],
            'converted_filename': record[4],
            'original_filepath': record[5],
            'converted_filepath': record[6],
            'conversion_format': record[7],
            'status': record[8],
            'timestamp': record[8]
        } for record in tasks]
        

def __extract_task(task):
    return {
        'id': task[0],
        'original_filename': task[3],
        'converted_filename': task[4],
        'original_filepath': task[5],
        'converted_filepath': task[6],
        'conversion_format': task[7],
        'status': task[8],
        'timestamp': task[8]
    } 


@app.route('/api/tasks/list', methods=["GET"])
def list_tasks():
    with connection.cursor() as cr:
        cr.execute("SELECT * FROM tasks")
        return jsonify({"tasks": __extract_tasks(tasks=cr.fetchall())}), 200


@app.route('/api/tasks/retrieve/<task_id>', methods=["GET"])
def retrive_task(task_id):
    with connection.cursor() as cr:
        cr.execute(f"SELECT * FROM tasks where id = {task_id}")
        return jsonify({"task": __extract_task(task=cr.fetchone())})
    



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
    
    

@app.route('/api/upload/<filename>', methods=['POST'])
def upload_file():
    # try create new task with the file 
    pass
"""