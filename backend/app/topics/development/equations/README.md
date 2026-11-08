# Nimsara — Equations

Implemented as `equations`; application registration and readiness are pending Nadula's central integration review. The shared registry is restored to its prior state, with Equations unregistered and `ready=False`.

## Supported mathematics

- Easy: one-variable linear equations with the variable on one side.
- Medium: linear equations with variables on both sides.
- Hard: bracketed linear equations, signed coefficients and possible rational solutions.

Each generated question has four distinct shuffled options with opaque UUIDs. Exact `Fraction` arithmetic independently checks the unique solution, each diagnostic distractor, canonical statement and worked explanation. The validator accepts bounded integer-coefficient templates only; it never evaluates source text as Python or passes untrusted strings to a symbolic evaluator. Invalid or duplicate variants are rejected.

Diagnostic choices signal possible inverse-sign errors, missing division or a negated solution. One selection does not prove a misconception. Feedback includes trusted steps and specific teacher guidance.

Unsupported: quadratic/simultaneous equations, inequalities, variable denominators, identities, equations without a solution, word problems, free-text and handwritten answers.

## Manual and AI operation

Manual mode is the default and works offline. The topic's settings are independent of Binomial. An optional Ollama adapter uses the existing `httpx` dependency; no new SDK is required. Put settings in your ignored backend environment or process environment:

```dotenv
MATHROOT_EQUATIONS_MODE=manual
MATHROOT_EQUATIONS_PROVIDER=ollama
MATHROOT_EQUATIONS_MODEL=
MATHROOT_EQUATIONS_BASE_URL=http://127.0.0.1:11434
MATHROOT_EQUATIONS_TIMEOUT_SECONDS=4
MATHROOT_EQUATIONS_API_KEY=
```

To enable AI, select `MODE=auto` and set `MODEL` to a model available on your Ollama server. `API_KEY` is optional for an authenticated compatible endpoint; never commit credentials or put them in frontend settings. Other provider names are rejected and generation falls back to manual. No request occurs on import.

The model proposes only a bounded equation source. The module derives its options, key and explanation locally, independently of model claims. HTTP errors, missing configuration, invalid JSON/schema, invalid mathematics and oversized responses fall back to manual generation. Timeouts are bounded to 0.1–4 seconds (invalid values use 4). Responses are limited to 32 KB.

Answer analysis uses this topic's adapter through the shared verifier. Grades remain deterministic; inconsistent grades, unsupported diagnoses, low confidence or ungrounded prose are rejected. `MATHROOT_ANSWER_VERIFIER=manual` disables AI feedback globally. Model requests contain mathematical context only, with no user identity, sessions or database keys.

## English and Sinhala

`presentation.py` supplies Sinhala templates for instructions, checked working, feedback, corrective guidance and teacher recommendations without a model. Canonical expressions, options, IDs and grades stay unchanged. Unknown historical wording stays English with a translation warning.

An optional topic-owned translation adapter retains mathematical placeholders and uses the same bounded provider connection. The shared guard rejects missing/reordered tokens and new mathematical content. Semantic validation accepts only exact equivalents of known topic templates; arbitrary fluent output is insufficient. AI translation cannot change an answer or invent approved wording.

## Testing

From the repository root:

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m pytest tests/test_equations.py -q -p no:cacheprovider
Pop-Location
```

With the virtual environment activated, the requested command from `backend` is `python -m pytest -q tests/test_equations.py`.

Tests cover at least 100 generated variants per difficulty, independent substitution of every option, exact misconception values, identities/no-solution rejection, tampered questions, provider success/timeouts/bad JSON/schema/invalid mathematics/oversized responses, missing configuration, incorrect AI grades, rule-based feedback fallback, bilingual math preservation, translation rejection and assessment submission/reporting. Assessment tests temporarily register Equations using pytest's monkeypatch; production registration remains pending. Database persistence is verified with the shared in-memory Supabase double, not a live database. HTTP provider tests are mocked; no live model or credentials are required. Application fixtures require the shared backend's Supabase and python-dotenv dependencies in the local test environment.

Shared-suite expectations, application routes, frontend and Supabase integration belong to Nadula and are outside this topic cleanup.

Final topic check (2026-11-06): `python -m pytest -q tests/test_equations.py` from `backend`, using the repository-local virtual environment: **59 passed, 1 warning in 0.71s**. The warning is a dependency deprecation from Starlette's HTTPX TestClient. No shared tests were changed or run for this topic cleanup.

### Live provider limitation

The local Ollama discovery request (`GET http://127.0.0.1:11434/api/tags`) could not connect during this cleanup, and no Equations model was configured. A successful live generation/feedback request could not be verified. Mocked adapter tests establish validation and fallback behavior, not that a real model is installed or configured. To perform a live check, start Ollama, set `MATHROOT_EQUATIONS_MODE=auto` and `MATHROOT_EQUATIONS_MODEL` to an installed model, then call `ai.generate_question` directly and inspect `verification_method` from the topic verifier; a successful fallback alone is not evidence of live AI success.
