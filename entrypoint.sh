#!/bin/bash

sleep 20

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
service nginx start
gunicorn rest_api.wsgi -b 0.0.0.0:9000
