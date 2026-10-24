# __init__.py — code explained

**Source:** [backend/app/topics/__init__.py](../../../../backend/app/topics/__init__.py) · [All backend explanations](../../SOURCE_INDEX.md)

**What and how:** TOPICS maps ready IDs to generator objects; PLANNED_TOPICS supplies names/owners/readiness to the UI. Only Binomial is active.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–13: Code section

```python
"""Each teammate adds a topic module here without changing API routes."""
from app.topics.development.binomial.generator import LLMBinomialTopic
TOPICS = {
      "binomial": LLMBinomialTopic(),
}

PLANNED_TOPICS = [
    {'id': 'binomial', 'name': 'Binomial Expressions', 'owner': 'Nadula', 'ready': True},
    {'id': 'factorization', 'name': 'Factors of Quadratic Expressions', 'owner': 'Bopage', 'ready': False},
    {'id': 'equations', 'name': 'Equations', 'owner': 'Nimsara', 'ready': False},
    {'id': 'algebraic_fractions', 'name': 'Algebraic Fractions', 'owner': 'Fernando', 'ready': False},
    {'id': 'indices_logs', 'name': 'Indices and Logarithms', 'owner': 'Sadeepa', 'ready': False},
]
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Connected files

Follow these imports to their matching code explanations:

- [app/topics/development/binomial/generator.py](development/binomial/generator.py.md)

## How to explain this file in the viva

“TOPICS maps ready IDs to generator objects; PLANNED_TOPICS supplies names/owners/readiness to the UI. Only Binomial is active.”
