# Bopage — Factors of Quadratic Expressions

This is an unfinished workspace for topic ID `factorization`. It is not registered or ready. No completed Mathematics implementation is provided.

1. **Question generation:** implement the provider call and JSON conversion in `ai.generate_question`; `generator.generate_question` validates AI questions and automatically tries the manual generator on AI errors. Keep the original `InternalQuestion` / `InternalOption` contract in `app/contracts.py`.
2. **Answer analysis:** implement `ai.analyze_answer` and use `verifier.verify_answer` for independent checks. It delegates to the existing shared verifier; do not duplicate grading or fallback. Stable misconception codes belong in `FactorizationTopic.misconception_definitions`. Attach codes only to justified distractors.
3. **Your provider:** choose Ollama, Gemini, OpenRouter or another service in `ai.py`. No provider or Nadula model is forced. Configure a finite HTTP timeout, validate structured output, and raise on service/validation failures. Shared verification accepts only grounded `Analysis` feedback and retains deterministic correctness. Never include student identities, auth tokens or database keys in model requests.
4. **Manual fallback:** implement `manual.generate_question`, `validate_question`, `feedback` and `teaching_recommendation`. The supplied MCQ checker compares the selected ID with the independently validated key. Use SymPy/deterministic rules appropriate to this topic, including domain restrictions. AI failure triggers fallback automatically once these TODOs are implemented. Until then, `NotImplementedError` is intentional.
5. **Independent testing:** add tests under `backend/tests/test_factorization.py`. Run from `backend`: `.\.venv\Scripts\python.exe -m pytest tests/test_factorization.py -q`. Mock provider success, timeout, bad JSON, wrong AI grade and missing credentials; verify manual fallback, unique options, explanations and every generated key (100 questions per difficulty). No test file or completed question is supplied here. Test direct functions without changing the registry.
6. **Register only when complete:** in `app/topics/__init__.py`, import `from app.topics.development.factorization.generator import FactorizationTopic`, add `"factorization": FactorizationTopic()` to `TOPICS`, and change only the corresponding `PLANNED_TOPICS` item to `ready: True`. Do not remove existing topics. The adapter already supplies the existing TopicModule methods and optional `answer_feedback_provider` hook. The shared FastAPI submission route uses that hook, so your own provider is used without frontend/database changes. Persistence, class permissions, results and teacher aggregation stay in the shared backend.

## Backend environment

Put real values in ignored `backend/.env` or your process environment, never in source files. Do not create `NEXT_PUBLIC_` keys. Environment files are not supplied with secrets.

```dotenv
MATHROOT_FACTORIZATION_MODE=auto
MATHROOT_FACTORIZATION_PROVIDER=your_chosen_provider
MATHROOT_FACTORIZATION_MODEL=your_chosen_model
MATHROOT_FACTORIZATION_BASE_URL=your_chosen_endpoint
MATHROOT_FACTORIZATION_API_KEY=your_private_key_if_needed
MATHROOT_FACTORIZATION_TIMEOUT_SECONDS=4
```

These are inputs for your implementation, not a prebuilt provider client. Parse/bound `timeout_seconds` before using it. Local Ollama normally needs no API key. Set `MATHROOT_FACTORIZATION_MODE=manual` to skip topic AI calls. Shared `MATHROOT_ANSWER_VERIFIER=manual` also skips AI verification for all topics; leave it `auto` to test your provider. Question generation mode here is independent of Nadula's `MATHROOT_GENERATOR`.

For a smoke check, from `backend` run:

```powershell
.\.venv\Scripts\python.exe -c "from app.topics.development.factorization.generator import FactorizationTopic; print(FactorizationTopic.topic_id)"
```

The import should work; generating or verifying a question intentionally raises until your TODOs are complete. Run the existing suite with `.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider` before integration.

References: `app/topics/development/binomial/manual.py`, `app/topics/development/binomial/generator.py`, `app/topics/base.py`, `app/answer_verification.py` and `docs/TOPIC_CONTRACT.md`. Use their inputs/outputs as examples, not a requirement to use their provider. Trusted worked explanations must be independently checked; do not execute untrusted mathematical input as Python.

## English and Sinhala without changing Mathematics

1. Implement reviewed bilingual wording in the topic class's `presentation_text(field, text, question=None, misconception=None)` hook in `generator.py`. Use complete known templates or deterministic structured data. Return Sinhala only for wording you have checked; return `None` otherwise. Cover question instructions, worked explanations, misconception feedback, corrective guidance and teaching recommendations. Keep this manual wording available with every AI service off.
2. Keep `InternalQuestion` canonical. Never generate a second question, change an option ID/order, rewrite a mathematical expression, or create a different correct key for Sinhala. Shared `app.presentation` adds response-only `translations.si` / `translation_warnings`; the frontend selects text immediately without a language API parameter or database change.
3. For optional dynamic prose, implement `ai.TopicTranslationProvider.translate(masked_text)` using your own configuration/provider. Preserve each `[[MATH_n]]` token exactly once in order, enforce a finite timeout, and raise on bad JSON/service failure. No provider or API key is supplied by this starter.
4. Implement `validate_translation(field, source, translated, question=None)` using reviewed pairs or deterministic topic templates. It must return exactly `True` before AI text is displayed. Placeholder checks alone cannot verify meaning. Its starter return value is `False`, so unfinished translation safely keeps English with a warning.
5. Test both reviewed manual wording and valid/invalid provider responses. Confirm unchanged IDs, expressions, correct keys and scores; reject missing/reordered tokens, added numbers/formulas, altered meaning and provider failure. Reuse the existing shared grader and fallback instead of translating an AI answer into a new key. Do not mark this topic ready until the Mathematics and both fallback/display paths are complete.

Use `binomial/presentation.py` as a template example, not a model/provider requirement. The shared `TranslationProvider` interface also permits a custom `cache_key` to distinguish provider/model settings. Approved results are cached in memory, but topic semantic validation runs again on reuse. Your topic's `MODE=manual` prevents its provider calls; reviewed wording should still work. Keep keys in your ignored backend environment and never in `NEXT_PUBLIC_` variables. See `docs/TOPIC_CONTRACT.md` for the full optional contract.
