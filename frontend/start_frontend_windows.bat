@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>&1
if errorlevel 1 (
  echo Node.js was not found. Install Node.js 20.9 or later.
  pause
  exit /b 1
)
if not exist "node_modules\next" (
  echo Installing frontend packages...
  call npm install
  if errorlevel 1 (
    echo npm install failed. Check your internet connection and the error above.
    pause
    exit /b 1
  )
)
echo Starting MathRoot UI at http://localhost:3000
call npm run dev
