from flask import Flask, request, session
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

import psycopg2


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


connection = psycopg2.connect(
    host="postgres",
    port=5432,
    user="flask_celery",
    password="flask_celery",
    database="flask_celery"
)


def __extract_tasks(tasks):
    return [
        {
            'id': record[0], 
            'source_uuid': record[1], 
            'source_name': record[2],
            'source_format': record[3],
            'target_format': record[4],
            'create_datetime': record[5],
            'start_convert': record[6],
            'end_convert': record[7],
            'status': record[8]
        } for record in tasks]
        

def __extract_task(task):
    return {
        'id': task[0], 
        'source_uuid': task[1], 
        'source_name': task[2],
        'source_format': task[3],
        'target_format': task[4],
        'create_datetime': task[5],
        'start_convert': task[6],
        'end_convert': task[7],
        'status': task[8]
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