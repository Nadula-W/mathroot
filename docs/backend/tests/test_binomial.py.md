# test_binomial.py — code explained

**Source:** [backend/tests/test_binomial.py](../../../backend/tests/test_binomial.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Generates many questions and checks mathematical invariants, unique options, hidden-answer responses and topic readiness.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–7: Code section

```python
import random
from dataclasses import asdict
from sympy import Symbol, simplify, sympify
from app.topics.development.binomial.manual import BinomialTopic
from app.assessments import public_detail

x = Symbol('x')
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 9–20: test_generated_answers_are_consistent()

```python
def test_generated_answers_are_consistent():
    generator = BinomialTopic(random.Random(7))
    for difficulty in ['easy', 'medium', 'hard']:
        for _ in range(100):
            q = generator.generate_question(difficulty)
            assert len(q.options) == 4
            assert len({o.id for o in q.options}) == 4
            assert len({o.text for o in q.options}) == 4
            assert q.correct_option_id in {o.id for o in q.options}
            assert next(o for o in q.options if o.id == q.correct_option_id).misconception is None
            assert simplify(sympify(q.source_expression) - sympify(q.correct_expression)) == 0
            assert len([o for o in q.options if o.misconception is None]) == 1
```

**Explanation:**

- Tests that generated answers are consistent. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Checks symbolic mathematical equivalence rather than matching display text.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 22–28: test_question_generation_hides_answer()

```python
def test_question_generation_hides_answer():
    question = BinomialTopic().generate_question('easy')
    detail = public_detail({'id': 'test', 'title': 'Test', 'class_id': 'class-A', 'questions': [asdict(question)]}, True)
    assert len(detail['questions'][0]['options']) == 4
    assert 'correct_option_id' not in str(detail)
    assert 'misconception' not in str(detail)
    assert 'explanation' not in str(detail)
```

**Explanation:**

- Tests that question generation hides answer. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 30–35: test_topic_ownership()

```python
def test_topic_ownership(client):
    topics = client.get('/api/topics').json()
    assert len(topics) == 5
    assert sum(item['ready'] for item in topics) == 1
    client.user.update(id='teacher', role='teacher', requested_role='teacher')
    assert client.post('/api/tests', json={'title': 'Invalid topic', 'class_id': 'demo3', 'topic_ids': ['equations'], 'questions_per_topic': 1}).status_code == 422
```

**Explanation:**

- Tests that topic ownership. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Connected files

Follow these imports to their matching code explanations:

- [app/assessments.py](../app/assessments.py.md)
- [app/topics/development/binomial/manual.py](../app/topics/development/binomial/manual.py.md)

## How to explain this file in the viva

“Generates many questions and checks mathematical invariants, unique options, hidden-answer responses and topic readiness.”
