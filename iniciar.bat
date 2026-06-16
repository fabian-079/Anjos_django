@echo off
echo ========================================
echo ANJOS - Sistema de Gestion
echo ========================================
echo.

echo [1/3] Ejecutando migraciones...
python manage.py migrate

echo.
echo [2/3] Inicializando datos...
python init_db.py

echo.
echo [3/3] Iniciando servidor...
echo.
echo Servidor disponible en: http://127.0.0.1:8000
echo.
echo Credenciales:
echo   Admin: admin@anjos.com / admin123
echo   Cliente: cliente@test.com / cliente123
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
python manage.py runserver
