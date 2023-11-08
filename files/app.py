import os

from flask import url_for, flash
from flask import jsonify

from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip

from celery import Celery


CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'


celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery.conf.task_default_queue = "defaul_queue"


@celery.task
def convert_file(data):
    file = data.get('file')
    conversion_format = data.get('conversion_format')

    if file.filename != '':
        if not conversion_format and not allowed_format(conversion_format):
            return jsonify({'error': 'Extensión de destino no especificada'}), 400

        upload_folder = "/uploads"
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


        converted_file_url = url_for('download_file', filename=output_filename)
        flash('Conversión exitosa', 'success')
        return jsonify({"converted_file_url": converted_file_url}), 400


UPLOAD_FOLDER = 'uploads'
ALLOWED_FORMATS = {'mp4', 'webm', 'avi', 'mpeg', 'wmv'}


def allowed_format(extension):
    return extension.lower() in ALLOWED_FORMATS


# @app.route("/api/download/<filename>")
# def download_file(filename):
#     try:
#         file_path = os.path.join(upload_folder, filename)
        
#         file_stat = os.stat(file_path)
#         permissions = stat.filemode(file_stat.st_mode)
#         app.logger.info(f"Permissions for {file_path}: {permissions}")

#         app.logger.info(
#             f'Uploads before download: {os.listdir(upload_folder)}'
#         )

#         absolute_path = os.path.abspath(file_path)
#         return send_file(absolute_path, as_attachment=True)
#     except FileNotFoundError:
#         app.logger.info(
#             f'Contenido del directorio "uploads" después de no encontrar el archivo: {os.listdir(upload_folder)}'
#         )
#         return "Archivo no encontrado", 404
    
    

# @app.route('/api/upload/<filename>', methods=['POST'])
# def upload_file():
#     # try create new task with the file 
#     pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
