# 1. Usamos una versión oficial y ligera de Python 3.12
FROM python:3.12-slim

# 2. Evita que Python escriba archivos .pyc y fuerza a que muestre los logs de inmediato
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia los archivos de dependencias e instálalos
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# 6. Copia el resto del código del proyecto
COPY . /app/

# 7. Ejecuta collectstatic para preparar los archivos CSS/JS/Logo en /app/staticfiles/
RUN python manage.py collectstatic --noinput

# 8. Expone el puerto 8000
EXPOSE 8000

# 9. Comando para arrancar en producción usando Gunicorn (más rápido y seguro)
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]