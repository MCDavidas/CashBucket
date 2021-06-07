#!/bin/sh

set -e

python manage.py collectstatic --noinput

# uwsgi --socket :8000 --master --enable-threads --module mysite.wsgi
uwsgi --ini /app/mysite_uwsgi.ini
