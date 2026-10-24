# Independent topic workspaces

| Member | Folder | Topic ID |
| --- | --- | --- |
| Nadula | [binomial](binomial/README.md) | `binomial` |
| Bopage | [factorization](factorization/README.md) | `factorization` |
| Nimsara | [equations](equations/README.md) | `equations` |
| Fernando | [algebraic_fractions](algebraic_fractions/README.md) | `algebraic_fractions` |
| Sadeepa | [indices_logs](indices_logs/README.md) | `indices_logs` |

The four starter folders each contain `generator.py`, `verifier.py`, `ai.py`, `manual.py` and member instructions. The small `__init__.py` files make imports explicit. Start with your folder's README. Binomial contains Nadula's existing working implementation and remains registered and ready. The other four topics remain unregistered placeholders. No provider is contacted on import.

Complete and test the manual mathematics first, then implement your chosen provider. AI generation errors automatically attempt manual generation; answer analysis reuses the existing shared verifier and fallback. The existing optional `answer_feedback_provider()` hook selects each completed topic's provider without changing shared routes or pages. The obsolete single-file topic placeholders have been removed; develop only in these folders.

## Bilingual development

Keep one canonical question and verified key. Each starter's topic adapter contains small optional `presentation_text`, `translation_provider` and `validate_translation` hooks; `ai.py` contains a translation-provider TODO using that member's own configuration. Implement reviewed Sinhala templates first so manual fallback works without a model. Dynamic translation is allowed only after shared mathematical-placeholder checks and topic-owned semantic approval. Returning `None` / `False` safely retains English with a missing-translation warning.

Binomial's `presentation.py` is the working reference. Shared response metadata is supplied by `app.presentation`, and the frontend's existing selector uses it without changing test IDs or requesting a new question. The four unfinished topics remain unregistered and not ready. See each member README and `docs/TOPIC_CONTRACT.md` before extending the hooks.
