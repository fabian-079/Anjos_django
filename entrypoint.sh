#!/bin/bash
# 1. Recolectar estáticos (aquí sí tenemos acceso a las variables de entorno)
python manage.py collectstatic --noinput

# 2. Aplicar migraciones
python manage.py migrate --noinput

# 3. Iniciar el procesador de tareas
python manage.py process_tasks &

# 4. Iniciar Gunicorn
exec gunicorn wsgi:application --bind 0.0.0.0:8000