import os
import json

from flask import url_for, flash
from flask import jsonify

from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip

# from celery import Celery
from google.cloud import storage

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1


# CELERY_BROKER_URL = "redis://redis:6379/0"
# CELERY_RESULT_BACKEND = "redis://redis:6379/0"

os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


# celery = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# celery.conf.task_default_queue = "defaul_queue"

project_id = os.getenv("PROJECT_ID")
timeout = 600

UPLOAD_FOLDER = "uploads"
ALLOWED_FORMATS = ["mp4", "webm", "avi", "mpeg", "wmv"]


def __get_storage_client():
    return storage.Client.from_service_account_json(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )



def __convert_video(output_path, output_format, video):
    if output_format == "mp4":
        video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    elif output_format == "webm":
        video.write_videofile(output_path, codec="libvpx", audio_codec="libvorbis")
    elif output_format == "avi":
        video.write_videofile(output_path, codec="libxvid", audio_codec="mp3")
    elif output_format == "mpeg":
        video.write_videofile(output_path, codec="mpeg4", audio_codec="mp3")
    elif output_format == "wmv":
        video.write_videofile(output_path, codec="wmv2", audio_codec="wmav2")


def __uploaded_converted_file(result_file_name):
    storage_client = __get_storage_client()
    bucket = storage_client.get_bucket(os.getenv("BUCKET_NAME"))
    with open(result_file_name, "rb") as f:
        uploaded_blob = bucket.blob(result_file_name)
        uploaded_blob.upload_from_file(f)


def transform_video(message: pubsub_v1.subscriber.message.Message) -> None:
    data = message.data.decode("utf-8")
    data = json.loads(data)
    
    file_name = data.get("file_name")
    conversion_format = data.get("conversion_format")
    result_file_name = f"converted_{file_name.split('.')[0]}.{conversion_format}"
    storage_client = __get_storage_client()

    blobs = storage_client.list_blobs(os.getenv("BUCKET_NAME"))

    for b in blobs:
        if b.name == file_name:
            b.download_to_filename(b.name)

    if conversion_format in ALLOWED_FORMATS:
        video = VideoFileClip(file_name)

        __convert_video(
            output_path=result_file_name, output_format=conversion_format, video=video
        )

        __uploaded_converted_file(result_file_name=result_file_name)

    message.ack()

if __name__ == "__main__":    
    subscriber = pubsub_v1.SubscriberClient()

    subscription_path = subscriber.subscription_path(
        project_id,
        os.getenv("CONVERT_SUBSCRIPTION_ID")
    )

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=transform_video)
    print(f"Listening for messages on {subscription_path}..\n")

    with subscriber:
        try:
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
            streaming_pull_future.result()

