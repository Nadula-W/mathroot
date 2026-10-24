# generator.py — code explained

**Source:** [backend/app/topics/development/equations/generator.py](../../../../../../backend/app/topics/development/equations/generator.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** equations: Connects this member's AI/manual generators and supplies the TopicModule adapter. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–6: Code section

```python
"""Nimsara: AI-first question generation and the existing TopicModule adapter.

Unfinished: do not register this topic until manual and AI paths are validated.
"""
from app.contracts import InternalQuestion
from . import ai, manual
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 9–26: generate_question()

```python
def generate_question(difficulty: str) -> InternalQuestion:
    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    # The topic's mode is independent of Nadula's question-generation settings.
    if ai.configuration()["mode"] == "manual":
        question = manual.generate_question(difficulty)
    else:
        try:
            question = ai.generate_question(difficulty)
            # Never trust a provider's answer key without deterministic checking.
            manual.validate_question(question)
            return question
        except Exception:
            # Missing provider/model, timeout, bad schema or invalid mathematics.
            # Do not log API keys, prompts, provider bodies or student information.
            question = manual.generate_question(difficulty)
    manual.validate_question(question)
    return question
```

**Explanation:**

- In ai.py/manual.py this is an unfinished topic TODO. In generator.py it validates difficulty, tries AI plus mathematical validation, and falls back to the manual generator. The adapter class delegates to the same module-level function.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 29–33: EquationsTopic

```python
class EquationsTopic:
    topic_id = "equations"
    title = "Equations"
    # TODO: Populate with stable codes supported by your diagnostic distractors.
    misconception_definitions: dict[str, str] = {}
```

**Explanation:**

- Groups the fields/methods of EquationsTopic. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 35–36: generate_question()

```python
    def generate_question(self, difficulty: str) -> InternalQuestion:
        return generate_question(difficulty)
```

**Explanation:**

- In ai.py/manual.py this is an unfinished topic TODO. In generator.py it validates difficulty, tries AI plus mathematical validation, and falls back to the manual generator. The adapter class delegates to the same module-level function.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 38–39: feedback()

```python
    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        return manual.feedback(question, misconception)
```

**Explanation:**

- Returns the topic's trusted explanation of a possible mistake and worked procedure. In starter topics it is deliberately unfinished.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 41–42: teaching_recommendation()

```python
    def teaching_recommendation(self, misconception: str) -> str:
        return manual.teaching_recommendation(misconception)
```

**Explanation:**

- Maps a supported code to a teaching/practice activity. Starter topics must implement this; Binomial has working recommendations.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 44–46: answer_feedback_provider()

```python
    def answer_feedback_provider(self):
        # The shared verifier calls this optional hook after registration.
        return ai.TopicFeedbackProvider()
```

**Explanation:**

- Supplies the member's adapter to the existing shared verifier without new routes, pages or database fields.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Connected files

Follow these imports to their matching code explanations:

- [app/contracts.py](../../../contracts.py.md)
- [app/topics/development/equations/__init__.py](__init__.py.md)
- [app/topics/development/equations/ai.py](ai.py.md)
- [app/topics/development/equations/manual.py](manual.py.md)

## How to explain this file in the viva

“equations: Connects this member's AI/manual generators and supplies the TopicModule adapter. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.”
