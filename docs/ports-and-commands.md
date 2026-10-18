MATHROOT AI - RUNNING COMMANDS AND PORTS

Backend folder: mathroot\backend
Frontend folder: mathroot\frontend

1. START BACKEND (FASTAPI) - CMD TERMINAL 1

from backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Backend URL: http://127.0.0.1:8000
API Documentation: http://127.0.0.1:8000/docs
Health Check: http://127.0.0.1:8000/health

First-time backend setup (only if needed):
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

2. START FRONTEND (NEXT.JS) - CMD TERMINAL 2
--------------------------------------------
from frontend
npm run dev -- -p 3000

Homepage: http://localhost:3000
Student Interface: http://localhost:3000/student
Teacher Dashboard: http://localhost:3000/teacher

First-time frontend setup (only if needed):
npm install

3. PORT SUMMARY
---------------
Backend FastAPI: 8000
Swagger Docs: 8000
Frontend Next.js: 3000
Student Page: 3000
Teacher Page: 3000
SQLite: local database file; no network port

4. BACKEND API ROUTES
---------------------
GET  /health
GET  /api/topics
POST /api/questions/generate
POST /api/answers/submit
POST /api/practice/next
GET  /api/teacher/summary

5. RUN BACKEND TESTS
--------------------
cd /d "C:\Users\naduw\Desktop\ECS\year 3\sem2\BECS 32253 - Intelligent Systems\mathroot\backend"
.\.venv\Scripts\python.exe -m pytest -q

6. STOP SERVERS
---------------
Press Ctrl + C in the terminal running the server.

7. DAILY STARTUP (AFTER INITIAL INSTALLATION)
---------------------------------------------
Terminal 1: Open backend folder, then run:
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

Terminal 2: Open frontend folder, then run:
npm run dev

Keep both terminal windows open while testing the full application.
These are local development commands, not production deployment commands.