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
