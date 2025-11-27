@echo off
REM === Arranque del MCP Host (Interfaz gráfica) ===
cd /d %~dp0

REM Crear entorno virtual si no existe
if not exist .venv (
  echo [INFO] Creando entorno virtual...
  python -m venv .venv
)

REM Activar el entorno
call .venv\Scripts\activate

REM Iniciar la GUI
echo [INFO] Iniciando la aplicación (ventana)...
python host_gui.py

echo [FIN] Host finalizado.
pause
