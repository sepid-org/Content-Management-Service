#!/bin/sh

set -e

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    counter=0
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
        counter=$((counter+1))
        if [ $counter -ge 300 ]; then
            echo "Error: Could not connect to PostgreSQL within 30 seconds."
            exit 1
        fi
    done

    echo "PostgreSQL started"
fi

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear
echo "Static files collected."

exec gunicorn your_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
