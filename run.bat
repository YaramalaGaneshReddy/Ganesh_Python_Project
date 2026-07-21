@echo off
echo Starting Ganesh Store E-Commerce Application...
cd /d "%~dp0"
start "" http://127.0.0.1:8000/
.\venv\Scripts\python.exe manage.py runserver 8000
pause
