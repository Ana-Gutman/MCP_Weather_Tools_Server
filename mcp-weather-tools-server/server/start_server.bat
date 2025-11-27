@echo off
REM === Arranque del MCP Server ===
cd /d %~dp0

REM Crear venv si no existe
if not exist .venv (
  echo [INFO] Creando entorno virtual...
  python -m venv .venv
)

REM Activar venv
call .venv\Scripts\activate

REM Instalar dependencias
echo [INFO] Instalando dependencias del server...
pip install -r requirements.txt

REM Iniciar el server
echo [INFO] Iniciando server...
python server.py

REM Mantener ventana abierta si algo falla
echo [FIN] Server finalizado.
pause
