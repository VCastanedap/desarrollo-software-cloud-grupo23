# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /broker

# Copy the current directory contents into the container at /app
COPY . /broker

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the Celery worker when the container launches
# CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
CMD watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A app worker --concurrency=1 --loglevel=INFO -E