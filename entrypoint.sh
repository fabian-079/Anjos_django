#!/bin/bash
# Iniciar el procesador de tareas en segundo plano
python manage.py process_tasks &

# Iniciar Gunicorn (el servidor web)
exec gunicorn wsgi:application --bind 0.0.0.0:8000