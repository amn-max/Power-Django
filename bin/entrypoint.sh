#!/bin/bash
#python manage.py test
echo "migrating"
python manage.py collectstatic --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input
pipenv run gunicorn power.wsgi:application --bind 0.0.0.0:8000
exec "$@"