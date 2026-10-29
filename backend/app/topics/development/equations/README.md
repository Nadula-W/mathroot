# Nimsara — Equations

Implemented and registered as `equations` in `app/topics/__init__.py`. Other members' implementations are unchanged.

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
..\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
Pop-Location
```

Tests cover at least 100 generated variants per difficulty, independent substitution of every option, tampered questions, provider success/timeouts/bad JSON/schema/invalid mathematics/oversized responses, missing configuration, incorrect AI grades, bilingual math preservation, translation rejection and full assessment submission/reporting. HTTP is mocked; no live model or credentials are required. Full application fixtures also require the shared backend's Supabase dependency, installed in the local test environment.

Two pre-existing tests assume Binomial is the only ready topic (in `test_binomial.py` and `test_bilingual_assessments.py`). Those assertions are obsolete after registering Equations. They are left untouched to preserve other members' work; the equations assessment tests verify the new registration and behavior.
