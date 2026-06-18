#!/usr/bin/env python
"""
Script para configurar variables de entorno específicas para Railway
y evitar el RecursionError en background tasks.
"""

import os
import sys

def configure_railway_environment():
    """Configura variables de entorno específicas para Railway"""
    
    # Configuración de logging para Railway
    os.environ.setdefault('DJANGO_LOG_LEVEL', 'INFO')
    
    # Configuración de background tasks para Railway
    os.environ.setdefault('BACKGROUND_TASK_MAX_ATTEMPTS', '3')
    os.environ.setdefault('BACKGROUND_TASK_RUN_ASYNC', 'True')
    
    # Configuración de email para Railway (valores por defecto)
    if not os.environ.get('EMAIL_HOST'):
        os.environ.setdefault('EMAIL_HOST', 'smtp.gmail.com')
        os.environ.setdefault('EMAIL_PORT', '587')
        os.environ.setdefault('EMAIL_USE_TLS', 'True')
    
    print("Configuración de Railway aplicada")

if __name__ == '__main__':
    configure_railway_environment()
