# verifier.py — code explained

**Source:** [backend/app/topics/development/algebraic_fractions/verifier.py](../../../../../../backend/app/topics/development/algebraic_fractions/verifier.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** algebraic_fractions: Connects independent manual checking to the existing shared verifier. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–5: Code section

```python
"""Fernando: independent topic checks using the existing shared verifier."""
from app.answer_verification import verify_answer as shared_verify_answer
from app.contracts import InternalQuestion
from . import manual
from .generator import AlgebraicFractionsTopic
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 8–14: verify_answer()

```python
def verify_answer(question: InternalQuestion, option_id: str) -> dict:
    # Independently validate generated mathematics and the submitted option.
    # No AI opinion can change this deterministic key check.
    manual.verify_answer(question, option_id)
    # Reuse shared grading, output validation, confidence checks and automatic
    # fallback; this topic's optional provider hook selects its own provider.
    return shared_verify_answer(question, option_id, AlgebraicFractionsTopic())
```

**Explanation:**

- First calls the topic's deterministic manual checker, then invokes the shared verification service with this topic object. No grading/fallback system is duplicated.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 17–21: Code section

```python
# TODO: Define diagnostic codes in AlgebraicFractionsTopic.misconception_definitions,
# attach them to evidence-bearing distractors in your generators, and implement
# feedback/teaching actions in manual.py. Do not invent diagnoses from no evidence.
# For future free-text input, use a bounded safe mathematical parser and explicit
# domain rules. Keep current MCQ request/response contracts unchanged.
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Connected files

Follow these imports to their matching code explanations:

- [app/answer_verification.py](../../../answer_verification.py.md)
- [app/contracts.py](../../../contracts.py.md)
- [app/topics/development/algebraic_fractions/__init__.py](__init__.py.md)
- [app/topics/development/algebraic_fractions/generator.py](generator.py.md)
- [app/topics/development/algebraic_fractions/manual.py](manual.py.md)

## How to explain this file in the viva

“algebraic_fractions: Connects independent manual checking to the existing shared verifier. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.”
