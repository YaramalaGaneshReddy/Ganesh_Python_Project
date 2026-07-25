Write-Host "Starting Ganesh Store E-Commerce Application..." -ForegroundColor Green
Set-Location $PSScriptRoot
Start-Process "http://127.0.0.1:8000/"
& "$PSScriptRoot\venv\Scripts\python.exe" "$PSScriptRoot\manage.py" runserver 8000
