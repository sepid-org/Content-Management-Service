#!/bin/bash

# Apply migrations first
python manage.py migrate

# Start the Gunicorn server with Uvicorn worker for ASGI
gunicorn content_management_service.asgi:application --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000