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
Frontend: npm run test:i18n
Frontend: npm run build
Optional disposable live API check (backend): .\.venv\Scripts\python.exe scripts/verify_assessments.py

Backend environment names (ignored backend/.env):
SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY (backend-only secret).
Frontend environment names (ignored frontend/.env.local):
NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY.
Never put private provider keys or the backend secret in NEXT_PUBLIC_ variables.

Manual fallback checks (backend environment; restart backend after changing settings):
MATHROOT_GENERATOR=manual
MATHROOT_ANSWER_VERIFIER=manual
The Binomial Sinhala templates work without Ollama. Language preference is saved
in browser localStorage under mathroot.language; no language-specific database
setting or migration is required. Optional translation settings/hooks are described
in TOPIC_CONTRACT.md and the member READMEs; provider keys stay in backend env.

See frontend/README.md for the bilingual browser acceptance checklist,
backend/README.md and answer-verification.md for fallback behaviour, and
API_CONTRACT.md for the actual authenticated assessment endpoints.
Press Ctrl+C in each server terminal to stop it.
