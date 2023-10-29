FROM python:3.9-slim

RUN apt-get update

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD [ "flask", "run", "--host=0.0.0.0", "--port=5001"]