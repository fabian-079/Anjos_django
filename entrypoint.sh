#!/bin/bash

# 1. Recolectar estáticos
python manage.py collectstatic --noinput

# 2. Aplicar migraciones
python manage.py migrate --noinput

# 3. Iniciar el procesador de tareas
# --duration=0: el worker no se detiene después de procesar una tarea
# --log-std: envía los logs del worker a la salida estándar para ver qué pasa en Railway
python manage.py process_tasks --duration=0 --log-std &

# 4. Iniciar Gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:8000