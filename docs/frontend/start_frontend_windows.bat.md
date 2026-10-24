# start_frontend_windows.bat — code explained

**Source:** [frontend/start_frontend_windows.bat](../../frontend/start_frontend_windows.bat) · [All frontend explanations](SOURCE_INDEX.md)

**What and how:** Windows startup shortcut: changes to this folder, checks Node, installs missing frontend packages and runs npm run dev. It does not start FastAPI.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–20: Code section

```bat
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
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## How to explain this file in the viva

“Windows startup shortcut: changes to this folder, checks Node, installs missing frontend packages and runs npm run dev. It does not start FastAPI.”
