# MathRoot AI

**BECS 32253 — Artificial Intelligence | Sri Lankan O/L Mathematics**

MathRoot AI is an English/Sinhala Mathematics assessment platform for Sri Lankan O/L students and teachers. It helps students understand their mistakes and helps teachers identify areas that need more practice.

- **Teachers** create classes, generate multiple-choice tests, share join codes and view student results and possible misconception patterns.
- **Students** join their teacher's class, complete or resume assigned tests, and review saved explanations and feedback.
- **AI and mathematical rules work together:** Ollama can propose Binomial question coefficients and assist with approved feedback. SymPy checks generated mathematics, and the backend grades against the saved answer key. Manual fallback keeps the implemented topic working when AI is unavailable.
- **English and Sinhala use the same assessment:** changing language changes the displayed wording while preserving question IDs, option order, answers and scores.

**Current status:** Binomial Expressions is implemented and ready. The other four Mathematics topics have independent starter folders and remain under development. Nadula maintains the shared application; each member develops one topic.

## Where to find what you need

Start here when you need setup instructions, a code explanation or guidance for a change.

| I need to… | Open this |
| --- | --- |
| Understand the whole project or prepare for the viva | [System overview and viva guide](docs/README.md) |
| Start the application, find ports or configure environment variables | [Ports and commands](docs/ports-and-commands.md) |
| Understand frontend pages, navigation and API calls | [Frontend guide](docs/frontend/README.md) |
| Read the explanation for a specific frontend source file | [Frontend code-by-code index](docs/frontend/SOURCE_INDEX.md) |
| Understand backend permissions, tests, saved results and mathematics | [Backend guide](docs/backend/README.md) |
| Read the explanation for a specific backend source file | [Backend code-by-code index](docs/backend/SOURCE_INDEX.md) |
| Find API endpoints and request/response formats | [API contract](docs/API_CONTRACT.md) |
| Understand grading, AI feedback and manual fallback | [Answer verification guide](docs/answer-verification.md) |
| Build or register a Mathematics topic | [Topic contract](docs/TOPIC_CONTRACT.md) and [member workspace index](backend/app/topics/development/README.md) |
| Understand English/Sinhala support | [Frontend language guide](docs/frontend/README.md) and [backend presentation guide](docs/backend/README.md) |
| Configure a member's own AI provider | Their topic README in the [ownership table below](#group-ownership) |
| Run automated checks or follow the browser checklist | [Frontend checks](docs/frontend/README.md) and [backend checks](docs/backend/README.md) |

The code-by-code indexes mirror the source folders: for example, `frontend/app/student/page.tsx` is explained in `docs/frontend/app/student/page.tsx.md`.

## How the parts connect

| Part | Responsibility | Source folder |
| --- | --- | --- |
| Next.js frontend | Pages, language selection and student/teacher interactions | [frontend/app](frontend/app/) |
| FastAPI backend | Authentication checks, class/test operations, grading and reports | [backend/app](backend/app/) |
| Supabase | Account authentication and persistent classes, questions and answers | [Authentication adapter](backend/app/supabase_auth.py) and [assessment routes](backend/app/assessments.py) |
| Topic modules | Question generation, mathematical validation and diagnostic feedback | [Member topic folders](backend/app/topics/development/) |

The normal flow is: **teacher creates a class and test → student joins and answers → backend verifies and saves → student and teacher view results.**

## Run on Windows (PowerShell)

You need Python 3.11+, Node.js/npm and an existing Supabase project with MathRoot's tables and authentication configured. The repository's verification migration does not create the complete database. See the [backend guide](docs/backend/README.md) for how the application uses those tables and account roles.

Open the project root in VS Code. In the first terminal:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install supabase python-dotenv
python -m uvicorn app.main:app --reload
```

If PowerShell blocks activation, use the virtual-environment Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install supabase python-dotenv
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The two additional packages are already used by the backend but are currently missing from `requirements.txt`; include them for a fresh environment.

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
│   ├── README.md                # System overview and viva starting point
│   ├── frontend/                # Frontend overview and matching code explanations
│   ├── backend/                 # Backend overview and matching code explanations
│   ├── API_CONTRACT.md          # Assessment endpoints and payloads
│   ├── TOPIC_CONTRACT.md        # Topic implementation and registration rules
│   ├── answer-verification.md   # Grading, AI feedback and fallback
│   └── ports-and-commands.md    # Setup, local URLs and check commands
└── README.md
```

## Group ownership

Click a topic to open its implementation instructions and provider configuration.

| Member | Topic and instructions | Status | Extra responsibility |
| --- | --- | --- | --- |
| P.M.R.N.D.B. Wathurakumbura (Nadula) | [Grade 10 — Binomial Expressions](backend/app/topics/development/binomial/README.md) | Ready | Student UI, teacher dashboard, central integration |
| T.B. Bopage | [Grade 10 — Factors of Quadratic Expressions](backend/app/topics/development/factorization/README.md) | Under development | Full topic AI module |
| H.G.T. Nimsara | [Grade 10 — Equations](backend/app/topics/development/equations/README.md) | Under development | Full topic AI module |
| G.S.R.P. Fernando | [Grade 10 — Algebraic Fractions](backend/app/topics/development/algebraic_fractions/README.md) | Under development | Full topic AI module |
| T.G.R. Sadeepa | [Grade 11 — Indices and Logarithms](backend/app/topics/development/indices_logs/README.md) | Under development | Full topic AI module |

Each member implements their topic's generation, mathematical validation, misconception feedback, bilingual wording and manual fallback. Complete and test a topic before marking it ready; follow the [topic contract](docs/TOPIC_CONTRACT.md) for integration.

## Bilingual display and provider freedom

The existing top language selector defaults to English, saves `mathroot.language` in browser storage and updates the document language after mounting. It changes display text without recreating a test or resetting a selected answer. Backend responses retain canonical English fields and add optional Sinhala presentation data. Historical English records are translated on read where reviewed templates recognize them; stored questions and answer snapshots are preserved.

Binomial's reviewed Sinhala wording works without Ollama. Unknown prose can use the optional topic translation hook, subject to mathematical-token checks and topic-owned approval of the meaning; accepted text is cached. If safe Sinhala wording is unavailable, the original English remains visible with a missing-translation notice. AI never decides grades or rewrites answer identities.

Each member retains an independent provider configuration: Ollama, Gemini, OpenRouter, another API or manual-only operation. No paid translation provider or new internationalization dependency is required. Store API keys in ignored backend environment variables. The [topic contract](docs/TOPIC_CONTRACT.md) explains the small optional bilingual hooks.

The four unfinished topic folders provide starter interfaces; members still need to implement their selected provider clients and mathematical rules.

## Important milestones still to implement

1. Adaptive topic-specific diagnosis beyond simple difficulty changes; teacher-labelled sample data and probabilistic scoring.
2. Complete the four remaining Mathematics topics and their independently validated manual fallbacks.
3. Review Sinhala terminology with the group and evaluate provider-specific translation quality before extending beyond reviewed templates.
4. Broader browser acceptance, live-provider evaluation and deployment hardening.

Use disposable accounts for development and live workflow checks. Production readiness requires deployment and data-protection review beyond the automated test suite.
