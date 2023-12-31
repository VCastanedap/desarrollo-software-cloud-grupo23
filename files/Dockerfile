# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container to /app

RUN apt-get update -y && apt-get install -y \
    ffmpeg \
    libx264-dev \
    libvpx-dev \
    libxvidcore-dev \
    libvorbis-dev

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the Celery worker when the container launches
# CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
# CMD ["celery", "-A", "app", "worker", "--loglevel=info"]
CMD ["python", "app.py"]