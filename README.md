README - ProgramerAI_Agent 1.0.1

Descripción

ProgramerAI_Agent 1.0.1 es una herramienta desarrollada en Python que permite crear programas mediante Gemini AI, instalar sus dependencias y almacenarlas en la carpeta de perfiles. Esto permite generar y acceder a programas personalizados de manera sencilla. Además, facilita la importación de programas creados por la comunidad y su modificación a través de Gemini. También es posible guardar programas favoritos como perfiles por defecto en la configuración.

Requisitos

Antes de ejecutar el programa, asegúrese de cumplir con los siguientes requisitos:

Tener Python instalado (versión recomendada: 3.8 o superior).

Tener acceso a Google API (si es necesario para el uso de ciertos módulos).

Instalar las dependencias requeridas (se detallan en requirements.txt).

Instalación

Descargue o clone el repositorio en su sistema.

Ejecute install.bat o install + permisos pip.bat para instalar las dependencias necesarias.



Estructura del Proyecto

ProgramerAI_Agent-1.0.1
    |-- background.png                 # Imagen de fondo (si es utilizada en la interfaz)
    |-- config.txt                      # Archivo de configuración del programa
    |-- estructura_directorios.txt      # Descripción de la estructura de directorios
    |-- GoogleAPI.txt                   # Información sobre la configuración de Google API
    |-- install + permisos pip.bat      # Script de instalación con permisos adicionales
    |-- install.bat                     # Script de instalación de dependencias
    |-- ProgramerAI_Agent.py            # Archivo principal del programa
    |-- prompt_gemini.txt               # Prompt de uso para Gemini AI
    |-- prompt_gemini_exper.txt         # Prompt avanzado para Gemini AI
    |-- prompt_gemini_guion.txt         # Prompt para generación de guiones
    |-- prompt_gemini_instalaciones.txt # Prompt relacionado con instalaciones
    |-- requirements.txt                # Lista de dependencias necesarias
    |-- run.bat                         # Script para ejecutar el programa
    |
    |-- Perfiles                        # Carpeta con perfiles de organización
    |   |-- Organizador basico.py       # Perfil básico de organización
    |   |-- ReelOrganizerPro.py         # Perfil avanzado para organización de reels
    |   |-- Treeexporter.py             # Exportador de estructuras de directorios
    |   |-- Whisper.py                  # Integración con Whisper AI
    |
    |-- Reels                           # Carpeta para almacenamiento de reels
    |-- Temp                            # Carpeta temporal para archivos generados

Uso

Para ejecutar el programa:

Asegúrese de haber instalado las dependencias ejecutando install.bat o install + permisos pip.bat si pip no funciona correctamente.

Ejecute run.bat o inicie ProgramerAI_Agent.py manualmente con Python.

Contacto

Para soporte o consultas, contacte con el desarrollador o consulte la documentación en los archivos de configuración.

Versión: 1.0.1
Desarrollador: klinsec Anatine
