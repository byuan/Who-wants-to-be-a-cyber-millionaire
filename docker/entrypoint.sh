#!/bin/sh
set -eu

python manage.py migrate
python manage.py collectstatic --noinput

exec gunicorn cybermillionaire.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 4 --timeout 120
