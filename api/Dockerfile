# Use an official Python runtime as the base image
FROM python:3.9-slim

RUN apt-get update

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5001

# Run the Celery worker when the container launches
CMD [ "flask", "run", "--host=0.0.0.0", "--port=5001"]