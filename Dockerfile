# 1. Usamos una versión oficial y ligera de Python 3.12
FROM python:3.12-slim

# 2. Evita que Python escriba archivos .pyc y fuerza a que muestre los logs de inmediato
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instala las dependencias del sistema necesarias para compilar herramientas de Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia los archivos de dependencias e instálalos
# (Asumimos que usaremos requirements.txt, el cual crearemos en el siguiente paso)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6. Copia el resto del código del proyecto Anjos
COPY . /app/

# 7. Expone el puerto por el que escuchará la app (Railway maneja el puerto dinámicamente mediante variables de entorno)
EXPOSE 8000

# 8. Comando para arrancar el servidor en producción usando el archivo manage.py
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]