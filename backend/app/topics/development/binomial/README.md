# Nadula ? Binomial Expressions

This folder contains the existing working implementation, moved without changing its mathematics or behavior.

- `manual.py`: rule-based generation, SymPy validation, misconception feedback and teaching recommendations (`BinomialTopic`).
- `generator.py`: existing Ollama generation, configuration and automatic manual fallback (`LLMBinomialTopic`).
- Answer verification continues to use `app/answer_verification.py`; it is shared rather than duplicated here.

The topic remains registered and ready. Import the manual topic with `from app.topics.development.binomial.manual import BinomialTopic` and the AI generator with `from app.topics.development.binomial.generator import LLMBinomialTopic`.

Existing backend environment settings are unchanged: `MATHROOT_GENERATOR`, `MATHROOT_OLLAMA_MODEL`, and the separate `MATHROOT_ANSWER_*` settings. Store secrets only in ignored backend environment files.

From `backend`, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```
