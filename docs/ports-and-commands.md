MathRoot local development

Backend (from backend):
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Frontend (from frontend, separate terminal):
npm run dev -- -p 3000

URLs:
Frontend: http://localhost:3000
Student: http://localhost:3000/student
Teacher: http://localhost:3000/teacher
FastAPI docs: http://127.0.0.1:8000/docs
Health: http://127.0.0.1:8000/health
Ollama: http://127.0.0.1:11434
Database: hosted Supabase PostgreSQL; assessments do not use SQLite.

First-time setup:
Backend: py -m venv .venv
Backend: .\.venv\Scripts\python.exe -m pip install -r requirements.txt
Frontend: npm ci

Checks:
Backend: .\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
Frontend: npm run typecheck
Frontend: npm run build
Optional disposable live API check (backend): .\.venv\Scripts\python.exe scripts/verify_assessments.py

See assessment-workflow.md for environment variables, security, API contracts and acceptance steps.
Press Ctrl+C in each server terminal to stop it.
