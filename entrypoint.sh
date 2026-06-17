#!/bin/bash

# 1. Recolectar estáticos
python manage.py collectstatic --noinput

# 2. Aplicar migraciones
python manage.py migrate --noinput

# 3. Iniciar el procesador de tareas
# --duration=0: hace que el worker no se detenga después de procesar una tarea
# --queue: asegura que atienda la cola por defecto de forma continua
python manage.py process_tasks --duration=0 --queue &

# 4. Iniciar Gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:8000