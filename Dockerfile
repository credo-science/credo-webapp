FROM python:3.7-slim

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y gcc python3-dev default-libmysqlclient-dev
COPY . /app
WORKDIR /app
COPY local_settings.py credo/
RUN pip install -r requirements.txt
RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn", "--access-logfile", "-", "--workers", "4","--timeout", "60",\
     "--max-requests", "1000", "--max-requests-jitter", "100", "--worker-class", "gevent",\
     "--bind", "0.0.0.0:8080", "credo.wsgi:application", "--log-level", "debug"]

