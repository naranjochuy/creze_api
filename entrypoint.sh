#!/bin/bash

python manage.py collectstatic --no-input
python manage.py migrate
exec gunicorn -c config/gunicorn/conf.py \
     --bind :8000 \
     --chdir creze_api \
     creze_api.wsgi:application
