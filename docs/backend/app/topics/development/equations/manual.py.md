# manual.py — code explained

**Source:** [backend/app/topics/development/equations/manual.py](../../../../../../backend/app/topics/development/equations/manual.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** equations: Contains TODOs for deterministic mathematics, validation, feedback and teaching activities. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–2: Code section

```python
"""Nimsara: deterministic mathematics and fallback. No completed math is supplied."""
from app.contracts import InternalQuestion
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 5–10: generate_question()

```python
def generate_question(difficulty: str) -> InternalQuestion:
    # TODO: Generate an original syllabus-aligned question for this difficulty.
    # Return InternalQuestion with opaque UUIDs, four distinct InternalOption
    # values, one correct_option_id, explanation, source_expression and
    # correct_expression. Label diagnostic distractors with stable codes.
    raise NotImplementedError("Implement equations manual question generation.")
```

**Explanation:**

- In ai.py/manual.py this is an unfinished topic TODO. In generator.py it validates difficulty, tries AI plus mathematical validation, and falls back to the manual generator. The adapter class delegates to the same module-level function.
- This is a deliberate unfinished TODO. The topic/provider is not a completed mathematics implementation.

## Lines 13–18: validate_question()

```python
def validate_question(question: InternalQuestion) -> None:
    # TODO: Independently verify the key and every distractor using appropriate
    # deterministic mathematics/SymPy. Reject duplicates and invalid questions.
    # Check domain restrictions (e.g. nonzero denominators) where relevant.
    # Never eval, parse_expr or sympify untrusted provider/student strings.
    raise NotImplementedError("Implement equations mathematical validation.")
```

**Explanation:**

- An explicit TODO for topic-specific deterministic answer/distractor/domain checks. This must be complete before the topic becomes ready.
- This is a deliberate unfinished TODO. The topic/provider is not a completed mathematics implementation.

## Lines 21–26: verify_answer()

```python
def verify_answer(question: InternalQuestion, option_id: str) -> bool:
    """Deterministic MCQ verification against a mathematically validated key."""
    validate_question(question)
    if option_id not in {option.id for option in question.options}:
        raise ValueError("Unknown answer option.")
    return option_id == question.correct_option_id
```

**Explanation:**

- Calls validate_question, rejects an unknown selected option and compares its ID to the validated key. The topic-specific validation remains a TODO.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 29–33: feedback()

```python
def feedback(question: InternalQuestion, misconception: str | None) -> str:
    # TODO: Return trusted worked steps and a possible-misconception explanation.
    # None is used for correct selections; unknown wrong selections are handled
    # by the shared verifier. Never diagnose a misconception as proven.
    raise NotImplementedError("Implement equations manual feedback.")
```

**Explanation:**

- Returns the topic's trusted explanation of a possible mistake and worked procedure. In starter topics it is deliberately unfinished.
- This is a deliberate unfinished TODO. The topic/provider is not a completed mathematics implementation.

## Lines 36–39: teaching_recommendation()

```python
def teaching_recommendation(misconception: str) -> str:
    # TODO: Map your stable codes to specific correction/practice activities.
    # Include a safe generic recommendation for unknown codes.
    raise NotImplementedError("Implement equations teaching recommendations.")
```

**Explanation:**

- Maps a supported code to a teaching/practice activity. Starter topics must implement this; Binomial has working recommendations.
- This is a deliberate unfinished TODO. The topic/provider is not a completed mathematics implementation.

## Connected files

Follow these imports to their matching code explanations:

- [app/contracts.py](../../../contracts.py.md)

## How to explain this file in the viva

“equations: Contains TODOs for deterministic mathematics, validation, feedback and teaching activities. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.”
