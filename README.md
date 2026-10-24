# MathRoot AI

**BECS 32253 — Artificial Intelligence | Sri Lankan O/L Mathematics**

A shared Mathematics assessment application for the five-person group. **Nadula maintains the shared student and teacher interfaces; each member completes one topic module.**

The working Grade 10 Binomial Expressions module generates algebra questions, verifies them with SymPy, evaluates multiple-choice responses, records diagnostic signals and produces teacher summaries. Next.js provides student and teacher dashboards; FastAPI enforces class ownership and grading; Supabase supplies authentication and persistent assessment data. Four further topics remain unfinished development starters.

English and Sinhala share the same tests, questions, answer keys and scores. A lightweight language provider translates interface labels immediately. Reviewed Binomial templates supply Sinhala mathematics and manual feedback; optional validated AI translation can handle additional prose. Translation changes presentation only. See the [viva guide](docs/README.md), [frontend source explanations](docs/frontend/SOURCE_INDEX.md) and [backend source explanations](docs/backend/SOURCE_INDEX.md).

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

Start the frontend in another terminal:

```powershell
cd frontend
npm ci
npm run dev -- -p 3000
```

Configure the existing Supabase settings in ignored `backend/.env` and `frontend/.env.local`; keep the backend secret key out of frontend configuration. See [ports and commands](docs/ports-and-commands.md) for names and commands.

**First demo:** Sign in as an approved teacher, create a class and generate a Binomial test. Sign in as a student, join using the class ID/code, and open that test. Switch English / සිංහල before or after answering: IDs, options, progress and scores stay the same. The protected assessment API is documented in [API_CONTRACT.md](docs/API_CONTRACT.md).

## Run automated tests

From `backend` with your virtual environment active:

```powershell
python -m pytest -q
```

From `frontend`, run `npm run typecheck`, `npm run test:i18n` and `npm run build`. Language-specific focused checks and browser acceptance steps are described in the frontend/backend guides. Unit tests use mocked providers and a disposable in-memory database adapter; they do not require live student data.

## Repository layout

```text
mathroot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py               # Shared FastAPI routes
│   │   ├── contracts.py          # Common request/response models
│   │   ├── assessments.py        # Classes, tests, answers and results
│   │   ├── answer_verification.py # Shared deterministic grading and AI fallback
│   │   ├── presentation.py       # Reviewed/guarded translated response text
│   │   └── topics/
│   │       ├── base.py           # Topic interface
│   │       └── development/      # Member topic folders (Binomial is ready)
│   ├── tests/
│   └── requirements.txt
├── frontend/                    # Working Next.js student/teacher interfaces
│   ├── app/                     # Pages and shared components
│   └── lib/i18n/                # English/Sinhala dictionaries and language state
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

## Bilingual display and provider freedom

The existing top language selector defaults to English, saves `mathroot.language` in browser storage and updates the document language after mounting. It changes display text without recreating a test or resetting a selected answer. Backend responses retain canonical English fields and add optional Sinhala presentation data. Historical English records are translated on read where reviewed templates recognize them; stored questions and answer snapshots are preserved.

Binomial's reviewed Sinhala wording works without Ollama. Unknown prose can use the optional topic translation hook, subject to mathematical-token checks and topic-owned approval of the meaning; accepted text is cached. If safe Sinhala wording is unavailable, the original English remains visible with a missing-translation notice. AI never decides grades or rewrites answer identities.

Each member retains an independent provider configuration: Ollama, Gemini, OpenRouter, another API or manual-only operation. No paid translation provider or new internationalization dependency is required. Store API keys in ignored backend environment variables. The [topic contract](docs/TOPIC_CONTRACT.md) explains the small optional bilingual hooks.

## Important milestones still to implement

1. Adaptive topic-specific diagnosis beyond simple difficulty changes; teacher-labelled sample data and probabilistic scoring.
2. Complete the four remaining Mathematics topics and their independently validated manual fallbacks.
3. Review Sinhala terminology with the group and evaluate provider-specific translation quality before extending beyond reviewed templates.
4. Broader browser acceptance, live-provider evaluation and deployment hardening.

Use disposable accounts for development and live workflow checks. Production readiness requires deployment and data-protection review beyond the automated test suite.
