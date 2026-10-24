# Nadula — Binomial Expressions

This folder contains the existing working implementation. Question generation and grading remain unchanged; optional display hooks add English/Sinhala presentation.

- `manual.py`: rule-based generation, SymPy validation, misconception feedback and teaching recommendations (`BinomialTopic`).
- `generator.py`: existing Ollama generation, configuration and automatic manual fallback (`LLMBinomialTopic`).
- `presentation.py`: reviewed Sinhala instructions, worked explanations, misconception feedback and teaching recommendations. Matches known complete English templates using validated question data; never changes question IDs, options, answer keys or scores.
- Answer verification continues to use `app/answer_verification.py`; it is shared rather than duplicated here.

The topic remains registered and ready. Import the manual topic with `from app.topics.development.binomial.manual import BinomialTopic` and the AI generator with `from app.topics.development.binomial.generator import LLMBinomialTopic`.

Existing backend environment settings are unchanged: `MATHROOT_GENERATOR`, `MATHROOT_OLLAMA_MODEL`, and the separate `MATHROOT_ANSWER_*` settings. Store secrets only in ignored backend environment files.

## English and Sinhala display

`BinomialTopic.presentation_text(...)` delegates to the local reviewed templates. The shared `app/presentation.py` calls this after loading a question or verified feedback and adds `translations.si` / `translation_warnings` metadata to the response. The frontend selector chooses which wording to display without generating another question. Algebraic expressions and option order stay exactly the same.

Both current manual/AI-generated English wording and recognized historical Binomial templates receive Sinhala display. Old database records are not changed or regraded. If a historical sentence is unknown, English remains visible with a missing-translation notice. Manual generation and feedback remain available in Sinhala with Ollama off.

Optional AI translation uses `translation_provider()` and `validate_translation(...)`. `MATHROOT_TRANSLATION_MODE=manual` is the default. Set it to `auto` to permit the existing Ollama translation adapter; optional `MATHROOT_TRANSLATION_MODEL` selects a model and `MATHROOT_TRANSLATION_TIMEOUT_SECONDS` defaults to 2 (valid 0.1–4). Every accepted result must preserve masked mathematical tokens and match a reviewed equivalent. Do not weaken that semantic validation to accept arbitrary fluent text. Add newly reviewed wording to `presentation.py` instead.

No new package, SQL migration, separate language-specific question record or answer key is needed. Other members may use this template pattern without using this provider.

From `backend`, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

Focused bilingual API checks: `tests/test_bilingual_assessments.py`. Translation/template tests are listed in [the backend source index](../../../../../docs/backend/SOURCE_INDEX.md). Run with providers mocked and confirm that invalid/timeout output preserves English or reviewed manual wording and never changes grades.
