# base.py — code explained

**Source:** [backend/app/topics/base.py](../../../../backend/app/topics/base.py) · [All backend explanations](../../SOURCE_INDEX.md)

**What and how:** TopicModule describes the generation, feedback and teaching methods required from each completed topic. Protocol describes an interface without requiring inheritance.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.



**Bilingual update:** The required topic methods stay the same. The Protocol docstring describes optional presentation_text, translation_provider and validate_translation hooks without making them mandatory for every topic.

## Lines 1–5: Code section

```python
#Rules that all five members must followRules that all five members must follow
from typing import Protocol
from app.contracts import InternalQuestion


```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 6–17: TopicModule

```python
class TopicModule(Protocol):
    """Required mathematics contract; bilingual presentation remains optional.

    Completed topics may also expose presentation_text(field, text,
    question=None, misconception=None) for reviewed Sinhala templates, and
    translation_provider()/validate_translation(field, source, translated,
    question=None) for optional AI translation. These are display hooks only;
    the shared presentation service keeps canonical mathematics unchanged.
    """
    topic_id: str
    title: str

```

**Explanation:**

- Groups the fields/methods of TopicModule. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 18–21: generate_question()

```python
    def generate_question(self, difficulty: str) -> InternalQuestion:
        """Create an original, mathematically verified question."""
        ...

```

**Explanation:**

- In ai.py/manual.py this is an unfinished topic TODO. In generator.py it validates difficulty, tries AI plus mathematical validation, and falls back to the manual generator. The adapter class delegates to the same module-level function.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 22–25: feedback()

```python
    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        """Generate a concept-specific explanation after an answer."""
        ...

```

**Explanation:**

- Returns the topic's trusted explanation of a possible mistake and worked procedure. In starter topics it is deliberately unfinished.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 26–28: teaching_recommendation()

```python
    def teaching_recommendation(self, misconception: str) -> str:
        """A concrete next-class correction activity."""
        ...
```

**Explanation:**

- Maps a supported code to a teaching/practice activity. Starter topics must implement this; Binomial has working recommendations.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Connected files

Follow these imports to their matching code explanations:

- [app/contracts.py](../contracts.py.md)

## How to explain this file in the viva

“TopicModule describes the generation, feedback and teaching methods required from each completed topic. Protocol describes an interface without requiring inheritance.”
