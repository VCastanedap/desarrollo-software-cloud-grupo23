from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask import jsonify


import psycopg2


app = Flask(__name__)


connection = psycopg2.connect(
    host="34.28.55.3",
    port="5432",
    user="postgres",
    password="U{p;ky&~kN*Y_hv-",
    database="cloud-testing"
)



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
        'creation_date': task[8]
    } 


@app.route('/api/tasks/list', methods=["GET"])
def list_tasks():
    with connection.cursor() as cr:
        cr.execute("SELECT * FROM tasks")
        return jsonify({"tasks": __extract_tasks(tasks=cr.fetchall())}), 200


@app.route('/api/tasks/create', methods=["POST"])
def create_task():

    user_id=""
    file_name=""
    input_path=""
    output_file_name=""
    output_path=""
    conversion_format=""

    with connection.cursor() as cr:
        cr.execute(f"""
            INSERT INTO file_conversion_task (user_id, original_filename, original_filepath, converted_filename, converted_filepath, conversion_format, status)
            VALUES ({user_id}, {file_name}, {input_path}, {output_file_name}, {output_path}, {conversion_format}, 'available')
            RETURNING id
            """
        )
        return jsonify({"tasks": __extract_tasks(tasks=cr.fetchall())}), 200


@app.route('/api/tasks/retrieve/<task_id>', methods=["GET"])
def retrive_task(task_id):
    with connection.cursor() as cr:
        cr.execute(f"SELECT * FROM tasks where id = {task_id}")
        return jsonify({"task": __extract_task(task=cr.fetchone())})


@app.route('/api/tasks/delete/<task_id>', methods=["DELETE"])
def delete_task(task_id):
    with connection.cursor() as cr:
        cr.execute(f"SELECT * FROM tasks where id = {task_id}")
        return jsonify({"task": __extract_task(task=cr.fetchone())})
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001)
