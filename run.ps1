Write-Host "Starting Ganesh Store E-Commerce Application..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000/"
& ".\venv\Scripts\python.exe" manage.py runserver 8000
