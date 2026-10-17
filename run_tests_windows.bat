@echo off
setlocal
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (echo First run start_backend_windows.bat & pause & exit /b 1)
".venv\Scripts\python.exe" -m pytest -q
pause
