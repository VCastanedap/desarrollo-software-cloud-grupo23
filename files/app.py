from datetime import datetime
import os

from flask import Flask, request, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip

from celery import Celery
import psycopg2

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery.conf.task_default_queue = "defaul_queue"

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

conn = psycopg2.connect(
    host="postgres",
    port=5432,
    user="flask_celery",
    password="flask_celery",
    database="flask_celery"
)


    
cursor = conn.cursor()


# class FileConversionTask(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
#     user = db.relationship('User', backref=db.backref('file_conversion_tasks', lazy=True))
#     original_filename = db.Column(db.String(255), nullable=False)
#     converted_filename = db.Column(db.String(255))
#     original_filepath = db.Column(db.String(255), nullable=False)
#     converted_filepath = db.Column(db.String(255))
#     conversion_format = db.Column(db.String(20), nullable=False)
#     status = db.Column(db.String(20), default='unavailable')
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

"""
def task_by_id(id_task):
    print("** llegue -> ", request.method )
    if 'username' in session:
        
        if request.method == 'GET':
            task = FileConversionTask.query.filter_by(user_id=session['id_user'], id=id_task).first()

            if task is None:
                return 'Tarea no encontrada', 404  # Retorna un código 404 si la tarea no existe

            return render_template('id_tasks.html', username=session['id_user'], task=task)

        
        if request.method == 'DELETE':
            
            task = FileConversionTask.query.filter_by(user_id=session['id_user'], id=id_task).first()

            if task is None:
                return 'Tarea no encontrada', 404  # Retorna un código 404 si la tarea no existe
            
            # Elimina el archivo original y convertido del servidor
            if os.path.exists(task.original_filepath):
                os.remove(task.original_filepath)
            if os.path.exists(task.converted_filepath):
                os.remove(task.converted_filepath)
                
                
            db.session.delete(task)
            db.session.commit()
            return f'Tarea ID {id} eliminada: {task}'        

    return 'You are not logged in. <a href="/api/auth/login">Login</a> or <a href="/api/auth/register">Register</a>'
"""


@celery.task
def tasks(data):
    user_task_list = []
    user_tasks = {}

    file = data.get('file')
    conversion_format = data.get('conversion_format')
    username = data.get('username')
    user_id = data.get('user_id')


    if file.filename != '':
        if not conversion_format and not allowed_format(conversion_format):
            return jsonify({'error': 'Extensión de destino no especificada'}), 400

        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        os.chmod(file_path, 0o644)

        input_path = file_path
        output_filename = f"converted_{filename.rsplit('.', 1)[0]}.{conversion_format}"
        output_path = os.path.join(upload_folder, output_filename)

        video = VideoFileClip(input_path)
        video.write_videofile(output_path, codec='libx264')
        os.chmod(output_path, 0o644)

        user_task_list.append(f'Task: Convert {filename} to {conversion_format}')
        user_tasks[username] = user_task_list
        status="available"
        
        sql_query = """
            INSERT INTO file_conversion_task (user_id, original_filename, original_filepath, converted_filename, converted_filepath, conversion_format, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'available')
            RETURNING id
            """
        values = (user_id, filename, input_path, output_filename, output_path, conversion_format, status)

        cursor.execute(sql_query, values)
        conn.commit()

        # Obtén el ID de la fila insertada
        task_id = cursor.fetchone()[0]

        converted_file_url = url_for('download_file', filename=output_filename)
        flash('Conversión exitosa', 'success')

        # Obteniendo las tareas de conversión desde la base de datos
        sql_query = "SELECT * FROM file_conversion_task WHERE user_id = %s"
        values = (user_id,)

        cursor.execute(sql_query, values)
        file_conversion_tasks = cursor.fetchall()

        # return 'tasks.html', username=username, tasks=user_task_list, converted_file_url=converted_file_url, file_conversion_tasks=file_conversion_tasks)
        return jsonify(
            {
                "sername": username, 
                "tasks": user_task_list, 
                "converted_file_url": converted_file_url, 
                "file_conversion_tasks": file_conversion_tasks
            }
        ), 400


UPLOAD_FOLDER = 'uploads'
ALLOWED_FORMATS = {'mp4', 'webm', 'avi', 'mpeg', 'wmv'}


def allowed_format(extension):
    return extension.lower() in ALLOWED_FORMATS


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
