#!/bin/bash

nc -zvv mongodb 27017

service cron start
python manage.py crontab add
python manage.py makemigrations
python manage.py collectstatic --noinput
python manage.py migrate
service nginx start
gunicorn rest_api.wsgi -b 0.0.0.0:9000
