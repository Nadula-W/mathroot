# MathRoot AI — Starting Repository

**BECS 32253 — Artificial Intelligence | Sri Lankan O/L Mathematics**

A shared backend foundation for the five-person group. **Nadula builds the shared student and teacher interfaces; each member completes one topic module.**

This is **Milestone 1**, not the finished AI product. It includes one working Grade 10 Binomial Expressions module that generates new algebra questions, verifies them with SymPy, evaluates multiple-choice responses, records diagnostic signals, and produces a local teacher summary. Four further topics are placeholders.

## Run on Windows (PowerShell)

Install Python 3.11+ from python.org if needed. Open the project root in VS Code. Then:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

If PowerShell blocks activation, use the virtual-environment Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

- API documentation and **Try it out**: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Topics: http://127.0.0.1:8000/api/topics

**First demo:** In Swagger UI choose `POST /api/questions/generate`, then `POST /api/answers/submit`, and finally `GET /api/teacher/summary`. See `docs/API_CONTRACT.md`.

## Run automated tests

From `backend` with your virtual environment active:

```powershell
python -m pytest -q
```

## Repository layout

```text
mathroot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py               # Shared FastAPI routes
│   │   ├── contracts.py          # Common request/response models
│   │   └── topics/
│   │       ├── base.py           # Topic interface
│   │       └── development/      # Member topic folders (Binomial is ready)
│   ├── tests/
│   └── requirements.txt
├── frontend/                    # Nadula's future Next.js app
├── docs/
│   ├── API_CONTRACT.md
│   └── TOPIC_CONTRACT.md
└── README.md
```

## Group ownership

| Member | Topic | Extra responsibility |
|---|---|---|
| P.M.R.N.D.B. Wathurakumbura | Grade 10 — Binomial Expressions | Student UI, teacher dashboard, central integration |
| T.B. Bopage | Grade 10 — Factors of Quadratic Expressions | Full topic AI module |
| H.G.T. Nimsara | Grade 10 — Equations | Full topic AI module |
| G.S.R.P. Fernando | Grade 10 — Algebraic Fractions | Full topic AI module |
| T.G.R. Sadeepa | Grade 11 — Indices and Logarithms | Full topic AI module |

All members implement question generation, validation, misconception checks, adaptive questions, student corrections and teacher recommendations within their own topic.

## Important milestones still to implement

1. Adaptive topic-specific diagnosis beyond simple difficulty changes; teacher-labelled sample data and probabilistic scoring.
2. Optional LLM generation under syllabus constraints, with strict symbolic validation and output schema.
3. Student and teacher authentication, proper class ownership, data privacy and PostgreSQL.
4. Next.js student and teacher UIs, full end-to-end testing and evaluation.

This starter is intended for **local, pseudonymous testing only**, not production use.
