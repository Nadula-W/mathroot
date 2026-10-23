# Nimsara ? Equations

This is an unfinished workspace for topic ID `equations`. It is not registered or ready. No completed Mathematics implementation is provided.

1. **Question generation:** implement the provider call and JSON conversion in `ai.generate_question`; `generator.generate_question` validates AI questions and automatically tries the manual generator on AI errors. Keep the original `InternalQuestion` / `InternalOption` contract in `app/contracts.py`.
2. **Answer analysis:** implement `ai.analyze_answer` and use `verifier.verify_answer` for independent checks. It delegates to the existing shared verifier; do not duplicate grading or fallback. Stable misconception codes belong in `EquationsTopic.misconception_definitions`. Attach codes only to justified distractors.
3. **Your provider:** choose Ollama, Gemini, OpenRouter or another service in `ai.py`. No provider or Nadula model is forced. Configure a finite HTTP timeout, validate structured output, and raise on service/validation failures. Shared verification accepts only grounded `Analysis` feedback and retains deterministic correctness. Never include student identities, auth tokens or database keys in model requests.
4. **Manual fallback:** implement `manual.generate_question`, `validate_question`, `feedback` and `teaching_recommendation`. The supplied MCQ checker compares the selected ID with the independently validated key. Use SymPy/deterministic rules appropriate to this topic, including domain restrictions. AI failure triggers fallback automatically once these TODOs are implemented. Until then, `NotImplementedError` is intentional.
5. **Independent testing:** add tests under `backend/tests/test_equations.py`. Run from `backend`: `.\.venv\Scripts\python.exe -m pytest tests/test_equations.py -q`. Mock provider success, timeout, bad JSON, wrong AI grade and missing credentials; verify manual fallback, unique options, explanations and every generated key (100 questions per difficulty). No test file or completed question is supplied here. Test direct functions without changing the registry.
6. **Register only when complete:** in `app/topics/__init__.py`, import `from app.topics.development.equations.generator import EquationsTopic`, add `"equations": EquationsTopic()` to `TOPICS`, and change only the corresponding `PLANNED_TOPICS` item to `ready: True`. Do not remove existing topics. The adapter already supplies the existing TopicModule methods and optional `answer_feedback_provider` hook. The shared FastAPI submission route uses that hook, so your own provider is used without frontend/database changes. Persistence, class permissions, results and teacher aggregation stay in the shared backend.

## Backend environment

Put real values in ignored `backend/.env` or your process environment, never in source files. Do not create `NEXT_PUBLIC_` keys. Environment files are not supplied with secrets.

```dotenv
MATHROOT_EQUATIONS_MODE=auto
MATHROOT_EQUATIONS_PROVIDER=your_chosen_provider
MATHROOT_EQUATIONS_MODEL=your_chosen_model
MATHROOT_EQUATIONS_BASE_URL=your_chosen_endpoint
MATHROOT_EQUATIONS_API_KEY=your_private_key_if_needed
MATHROOT_EQUATIONS_TIMEOUT_SECONDS=4
```

These are inputs for your implementation, not a prebuilt provider client. Parse/bound `timeout_seconds` before using it. Local Ollama normally needs no API key. Set `MATHROOT_EQUATIONS_MODE=manual` to skip topic AI calls. Shared `MATHROOT_ANSWER_VERIFIER=manual` also skips AI verification for all topics; leave it `auto` to test your provider. Question generation mode here is independent of Nadula's `MATHROOT_GENERATOR`.

For a smoke check, from `backend` run:

```powershell
.\.venv\Scripts\python.exe -c "from app.topics.development.equations.generator import EquationsTopic; print(EquationsTopic.topic_id)"
```

The import should work; generating or verifying a question intentionally raises until your TODOs are complete. Run the existing suite with `.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider` before integration.

References: `app/topics/development/binomial/manual.py`, `app/topics/development/binomial/generator.py`, `app/topics/base.py`, `app/answer_verification.py` and `docs/TOPIC_CONTRACT.md`. Use their inputs/outputs as examples, not a requirement to use their provider. Trusted worked explanations must be independently checked; do not execute untrusted mathematical input as Python.
