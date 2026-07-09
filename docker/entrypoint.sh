#!/bin/sh

rm cybermillionaire/__init__.py
touch cybermillionaire/__init__.py

python manage.py migrate
python manage.py collectstatic

gunicorn cybermillionaire.wsgi:application --bind 0.0.0.0:8000
