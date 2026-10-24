# contracts.py — code explained

**Source:** [backend/app/contracts.py](../../../backend/app/contracts.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Shared dataclasses and Pydantic shapes. InternalQuestion includes hidden mathematical answers; public shapes omit them. Legacy student_id request models are not the active assessment submission schema.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–8: Code section

```python
"""Common contract that every mathematics-topic module must follow."""
from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel, Field

Difficulty = Literal['easy', 'medium', 'hard']

#Defining an answer option
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 9–13: InternalOption

```python
@dataclass(frozen=True)
class InternalOption:
    id: str
    text: str
    misconception: str | None = None
```

**Explanation:**

- One immutable server-side option: opaque ID, display text and optional supported misconception code.
- This dataclass is an immutable data container; asdict converts it for JSON storage.

## Lines 15–15: Code section

```python
#Defining a complete question
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 16–26: InternalQuestion

```python
@dataclass(frozen=True)
class InternalQuestion:
    id: str
    topic_id: str
    difficulty: str
    statement: str
    options: list[InternalOption]
    correct_option_id: str
    explanation: str
    source_expression: str
    correct_expression: str
```

**Explanation:**

- The immutable complete server-side question: IDs, text, options, hidden answer key, explanation and mathematical expressions.
- This dataclass is an immutable data container; asdict converts it for JSON storage.

## Lines 29–32: GenerateRequest

```python
class GenerateRequest(BaseModel):
    topic_id: str = 'binomial'
    difficulty: Difficulty = 'easy'
    class_id: str = Field(default='demo-class', min_length=1, max_length=64)
```

**Explanation:**

- A retained older/shared request shape. Current assessment routes use their own schemas; legacy student_id fields do not authorize active submissions.
- Pydantic checks these declared lengths, ranges or counts before route logic uses the input.

## Lines 35–37: PublicOption

```python
class PublicOption(BaseModel):
    id: str
    text: str
```

**Explanation:**

- Groups the fields/methods of PublicOption. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 40–46: PublicQuestion

```python
class PublicQuestion(BaseModel):
    question_id: str
    topic_id: str
    difficulty: str
    statement: str
    options: list[PublicOption]
    class_id: str
```

**Explanation:**

- Groups the fields/methods of PublicQuestion. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 49–52: AnswerRequest

```python
class AnswerRequest(BaseModel):
    question_id: str
    option_id: str
    student_id: str = Field(min_length=1, max_length=64)
```

**Explanation:**

- A retained older/shared request shape. Current assessment routes use their own schemas; legacy student_id fields do not authorize active submissions.
- Pydantic checks these declared lengths, ranges or counts before route logic uses the input.

## Lines 55–62: AnswerResult

```python
class AnswerResult(BaseModel):
    correct: bool
    selected_option: str
    correct_answer: str
    suspected_misconception: str | None
    diagnosis_status: str
    feedback: str
    recommended_next_difficulty: str
```

**Explanation:**

- Groups the fields/methods of AnswerResult. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 65–68: NextQuestionRequest

```python
class NextQuestionRequest(BaseModel):
    topic_id: str = 'binomial'
    class_id: str = 'demo-class'
    student_id: str = Field(min_length=1, max_length=64)
```

**Explanation:**

- A retained older/shared request shape. Current assessment routes use their own schemas; legacy student_id fields do not authorize active submissions.
- Pydantic checks these declared lengths, ranges or counts before route logic uses the input.

## How to explain this file in the viva

“Shared dataclasses and Pydantic shapes. InternalQuestion includes hidden mathematical answers; public shapes omit them. Legacy student_id request models are not the active assessment submission schema.”
