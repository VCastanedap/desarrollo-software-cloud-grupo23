import os

from flask import url_for, flash
from flask import jsonify

from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip

from celery import Celery
from google.cloud import storage


CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'


celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery.conf.task_default_queue = "defaul_queue"


def __get_storage_client():
    return storage.Client.from_service_account_json(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )


@celery.task
def upload_file(data):
    storage_client = __get_storage_client()

    bucket = storage_client.get_bucket(os.getenv('BUCKET_NAME'))

    blob = bucket.blob(f"uploaded_{data.get('file_name')}")
    
    with open(data.get('input_path'), 'rb') as f:
        blob.upload_from_file(f)
    
    return {
        "message": "Done", "status_code": 200
    }


def __convert_video(output_path, output_format, video):
    if output_format == 'mp4':
        video.write_videofile(output_path, codec='libx264', audio_codec='aac')
    elif output_format == 'webm':
        video.write_videofile(output_path, codec='libvpx', audio_codec='libvorbis')
    elif output_format == 'avi':
        video.write_videofile(output_path, codec='libxvid', audio_codec='mp3')
    elif output_format == 'mpeg':
        video.write_videofile(output_path, codec='mpeg4', audio_codec='mp3')
    elif output_format == 'wmv':
        video.write_videofile(output_path, codec='wmv2', audio_codec='wmav2')


@celery.task
def convert_file(data):
    storage_client = __get_storage_client()

    
    
    file_name = data.get('file_name')
    conversion_format = data.get('conversion_format')
    storage_client = __get_storage_client()

    blobs = storage_client.list_blobs(os.getenv('BUCKET_NAME'))
    
    for b in blobs:
        if b.name == file_name:
            b.download_to_filename(b.name)

    if conversion_format in ALLOWED_FORMATS:
        video = VideoFileClip(file_name)
        video.write_videofile(f"converted_{file_name.split('.')[0]}.{conversion_format}", codec='libvpx', audio_codec='libvorbis')


        bucket = storage_client.get_bucket(os.getenv('BUCKET_NAME'))
        with open(f"converted_{file_name.split('.')[0]}.{conversion_format}", 'rb') as f:
            uploaded_blob = bucket.blob(f"converted_{file_name.split('.')[0]}.{conversion_format}")
            uploaded_blob.upload_from_file(f)


UPLOAD_FOLDER = 'uploads'
ALLOWED_FORMATS = ['mp4', 'webm', 'avi', 'mpeg', 'wmv']


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
#
#
# LBO8h>edScYt/Jcd
# bdkJ1O_BtN0=oX40
