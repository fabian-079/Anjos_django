#!/bin/bash
# 1. Aplicar migraciones automáticamente al arrancar
python manage.py migrate --noinput

# 2. Iniciar el procesador de tareas en segundo plano
python manage.py process_tasks &

# 3. Iniciar Gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:8000