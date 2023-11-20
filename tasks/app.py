from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask import jsonify
from celery import Celery
import psycopg2

app = Flask(__name__)

# CELERY_BROKER_URL = "redis://redis:6379/0"
# CELERY_RESULT_BACKEND = "redis://redis:6379/0"

# celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# celery.conf.task_default_queue = "defaul_queue"


connection = psycopg2.connect(
    host="34.41.231.100",
    port="5432",
    user="postgres",
    password="bdkJ1O_BtN0=oX40",
    database="cloud-testing",
)


def __extract_tasks(tasks):
    return [
        {
            "id": record[0],
            "original_filename": record[3],
            "converted_filename": record[4],
            "original_filepath": record[5],
            "converted_filepath": record[6],
            "conversion_format": record[7],
            "status": record[8],
            "timestamp": record[8],
        }
        for record in tasks
    ]


def __extract_task(task):
    return {
        "id": task[0],
        "original_filename": task[3],
        "converted_filename": task[4],
        "original_filepath": task[5],
        "converted_filepath": task[6],
        "conversion_format": task[7],
        "status": task[8],
        "creation_date": task[8],
    }


@app.route("/api/tasks/list", methods=["GET"])
def list_tasks():
    with connection.cursor() as cr:
        cr.execute("SELECT * FROM tasks")
        return jsonify({"tasks": __extract_tasks(tasks=cr.fetchall())}), 200


def __build_upload_query(data):
    user_id = data.get("user_id")
    file_name = data.get("file_name")
    input_path = data.get("input_path")

    return f"""
        INSERT INTO tasks (user_id, original_filename, original_filepath, status)
        VALUES ({user_id}, '{file_name}', '{input_path}', 'uploading')
        RETURNING id
    """


def __build_convert_query(data):
    user_id = data.get("user_id")
    output_file_name = data.get("file_name")
    output_path = data.get("input_path")
    conversion_format = data.get("conversion_format")

    return f"""
        INSERT INTO tasks (user_id, converted_filename, converted_filepath, conversion_format, status)
        VALUES ({user_id}, '{output_file_name}', '{output_path}', '{conversion_format}', 'formatting')
        RETURNING id
    """


def __build_upload_event(data):
    return {
        "user_id": data.get("user_id"),
        "file_name": data.get("file_name"),
        "input_path": data.get("input_path"),
    }


def __build_convert_event(data):
    return {
        "user_id": data.get("user_id"),
        "file_name": data.get("file_name"),
        "input_path": data.get("input_path"),
        "conversion_format": data.get("conversion_format"),
    }


def __extract_create_task_result(data):
    return {"task_id": data[0]}


@app.route("/api/tasks/create", methods=["POST"])
def create_task():
    if request.json.get("task_type") == "upload_file":
        with connection.cursor() as cr:
            cr.execute(__build_upload_query(data=request.json))
            result = __extract_create_task_result(data=cr.fetchone())

        """
        celery.send_task(
            "app.upload_file",
            args=[__build_upload_event(data=request.json)],
            queue="defaul_queue",
        )
        """

        return {"msg": "Done", "task_id": result}, 201

    elif request.json.get("task_type") == "convert_file":
        with connection.cursor() as cr:
            cr.execute(__build_convert_query(data=request.json))
            result = __extract_create_task_result(data=cr.fetchone())

        """
        celery.send_task(
            "app.convert_file",
            args=[__build_convert_event(data=request.json)],
            queue="defaul_queue",
        )
        """

        return {"msg": "Done", "task_id": result}, 201


@app.route("/api/tasks/retrieve/<task_id>", methods=["GET"])
def retrive_task(task_id):
    with connection.cursor() as cr:
        cr.execute(f"SELECT * FROM tasks where id = {task_id}")
        return jsonify({"task": __extract_task(task=cr.fetchone())})


@app.route("/api/tasks/delete/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    with connection.cursor() as cr:
        cr.execute(f"SELECT * FROM tasks where id = {task_id}")
        return jsonify({"task": __extract_task(task=cr.fetchone())})



def __build_download_query(data):
    user_id = data.get("user_id")
    file_name = data.get("file_name")

    return f"""
        INSERT INTO tasks (user_id, original_filename, status)
        VALUES ({user_id}, '{file_name}', 'downloading')
        RETURNING id
    """


def __build_download_event(data):
    return {
        "user_id": data.get("user_id"),
        "file_name": data.get("file_name"),
    }


@app.route("/api/tasks/create/download", methods=["POST"])
def download_task():
    with connection.cursor() as cr:
        cr.execute(__build_download_query(data=request.json))
        result = __extract_create_task_result(data=cr.fetchone())

    """
    celery.send_task(
        "app.download_file",
        args=[__build_download_event(data=request.json)],
        queue="defaul_queue",
    )
    """
    return {"msg": "Done", "task_id": result}, 201



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001)
