# generator.py — code explained

**Source:** [backend/app/topics/development/algebraic_fractions/generator.py](../../../../../../backend/app/topics/development/algebraic_fractions/generator.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** algebraic_fractions: Connects this member's AI/manual generators and supplies the TopicModule adapter. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.



**Bilingual update:** The topic remains unfinished and unregistered. Small optional display hooks provide places for reviewed Sinhala templates, the member-owned translation provider and semantic approval. None/False intentionally keeps unsupported content in English until implemented.

## Lines 1–7: Code section

```python
"""Fernando: AI-first question generation and the existing TopicModule adapter.

Unfinished: do not register this topic until manual and AI paths are validated.
"""
from app.contracts import InternalQuestion
from . import ai, manual

```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 9–27: generate_question

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

## Lines 29–33: AlgebraicFractionsTopic

```python
class AlgebraicFractionsTopic:
    topic_id = "algebraic_fractions"
    title = "Algebraic Fractions"
    # TODO: Populate with stable codes supported by your diagnostic distractors.
    misconception_definitions: dict[str, str] = {}
```

**Explanation:**

- Groups the fields/methods of AlgebraicFractionsTopic. Declarations alone do not call a model or create database records; the following method sections explain execution.
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

## Lines 44–47: answer_feedback_provider()

```python
    def answer_feedback_provider(self):
        # The shared verifier calls this optional hook after registration.
        return ai.TopicFeedbackProvider()

```

**Explanation:**

- Supplies the member's adapter to the existing shared verifier without new routes, pages or database fields.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 49–53: presentation_text()

```python
    def presentation_text(self, field: str, text: str, question=None, misconception=None):
        # TODO: Match reviewed English/Sinhala templates by exact full text.
        # Cover statement, explanation, feedback and teaching recommendations.
        # Keep every mathematical expression unchanged. None means English + warning.
        return None
```

**Explanation:**

- Returns reviewed Sinhala wording for a complete known template, or None so unsupported text remains English with a warning. This hook changes presentation only.

## Lines 55–57: translation_provider()

```python
    def translation_provider(self):
        # Optional: use this topic's own provider, never Nadula's configuration.
        return ai.TopicTranslationProvider()
```

**Explanation:**

- Returns the topic-owned optional provider adapter. Binomial enables its existing Ollama adapter only in opt-in auto translation mode; other members retain their own provider choice.

## Lines 59–63: validate_translation()

```python
    def validate_translation(self, field: str, source: str, translated: str, question=None) -> bool:
        # TODO: Semantically approve only reviewed pairs or deterministic topic
        # templates. Placeholder checks alone cannot prove a translation correct.
        # Until implemented, all AI translations safely remain English.
        return False
```

**Explanation:**

- Must approve semantic meaning and return exactly True before dynamic AI text is shown. Binomial accepts reviewed equivalents; unfinished member stubs return False.

## Connected files

Follow these imports to their matching code explanations:

- [app/contracts.py](../../../contracts.py.md)
- [app/topics/development/algebraic_fractions/__init__.py](__init__.py.md)
- [app/topics/development/algebraic_fractions/ai.py](ai.py.md)
- [app/topics/development/algebraic_fractions/manual.py](manual.py.md)

## How to explain this file in the viva

“algebraic_fractions: Connects this member's AI/manual generators and supplies the TopicModule adapter. This starter is unregistered and unfinished; explicit NotImplementedError is intentional.”
