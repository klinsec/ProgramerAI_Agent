@echo off
REM Cambiar al directorio donde está el script
cd /d %~dp0
REM Activar el entorno virtual
call venv\Scripts\activate
REM Ejecutar la aplicación
python ProgramerAI_Agent.py
pause
