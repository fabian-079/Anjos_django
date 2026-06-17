import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# --- SEGURIDAD ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-anjos-jewelry-store-secret-key-change-in-production')
DEBUG = False

ALLOWED_HOSTS = [
    'anjosdjango-production.up.railway.app',
    '*.up.railway.app',
    'localhost',
    '127.0.0.1',
]

# --- APLICACIONES ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'infrastructure',
    'background_task', # Añadida para futuras tareas asíncronas
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'infrastructure.context_processors.unread_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# --- BASE DE DATOS ---
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'), conn_max_age=600, ssl_require=True)
}

# --- AUTENTICACIÓN ---
AUTH_USER_MODEL = 'infrastructure.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- IDIOMA Y TIEMPO ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS Y MEDIA ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

# --- CONFIGURACIONES ADICIONALES ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
CSRF_TRUSTED_ORIGINS = ['https://anjosdjango-production.up.railway.app']

# Email - Optimizaciones de Timeout añadidas
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10  # Detiene la espera después de 10 segundos para evitar 500 error
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'anjoscorreos@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'nicxihxjjzwjhnqb')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'ANJOS <anjoscorreos@gmail.com>')

# API Keys
EXCHANGE_RATE_API_KEY = os.environ.get('EXCHANGE_RATE_API_KEY', '')
EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'