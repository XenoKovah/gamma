#!/usr/bin/env sh

echo "Clearing .pyc files."
find /app/ -name "*.pyc" -delete
echo "Done."

echo "Starting development server."
cd /app/
python manage.py migrate
python manage.py runserver 0.0.0.0:9000
