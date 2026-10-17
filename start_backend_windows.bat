@echo off
setlocal
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -m venv .venv
    if errorlevel 1 (echo Python launcher not found. Install Python 3.11+ and try again. & pause & exit /b 1)
)
echo Installing Python dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (echo Dependency installation failed. & pause & exit /b 1)
echo.
echo Open http://127.0.0.1:8000/docs in your browser
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload
pause
