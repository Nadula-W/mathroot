# Nadula ? Binomial Expressions

This folder contains the existing working implementation, moved without changing its mathematics or behavior.

- `manual.py`: rule-based generation, SymPy validation, misconception feedback and teaching recommendations (`BinomialTopic`).
- `generator.py`: existing Ollama generation, configuration and automatic manual fallback (`LLMBinomialTopic`).
- Answer verification continues to use `app/answer_verification.py`; it is shared rather than duplicated here.

The topic remains registered and ready. Existing `from app.topics.binomial import BinomialTopic` imports still work. `app/topics/llm_binomial.py` is a compatibility re-export for older imports.

Existing backend environment settings are unchanged: `MATHROOT_GENERATOR`, `MATHROOT_OLLAMA_MODEL`, and the separate `MATHROOT_ANSWER_*` settings. Store secrets only in ignored backend environment files.

From `backend`, run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```
