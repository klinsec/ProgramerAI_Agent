@echo off
echo Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate
echo Actualizando pip...
pip install --upgrade pip
echo Instalando dependencias...
pip install -r requirements.txt
echo.

echo Abriendo Google AI Studio para obtener la API...
start https://aistudio.google.com/app/apikey
echo.

set /p API_KEY="Introduce tu API de Google: "
echo %API_KEY% > GoogleAPI.txt
echo.
echo Instalación completada.
pause