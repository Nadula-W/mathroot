# Common contract for every topic owner

The following module ownership has already been agreed:

| Owner | Module | Topic ID |
|---|---|---|
| Nadula | `app/topics/binomial.py` | `binomial` |
| Bopage | `app/topics/factorization.py` | `factorization` |
| Nimsara | `app/topics/equations.py` | `equations` |
| Fernando | `app/topics/algebraic_fractions.py` | `algebraic_fractions` |
| Sadeepa | `app/topics/indices_logs.py` | `indices_logs` |

Each topic implements the `TopicModule` interface in `app/topics/base.py`.

```python
class NewTopic:
    topic_id = 'your_topic_id'
    title = 'Your topic title'

    def generate_question(self, difficulty: str) -> InternalQuestion:
        ...

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        ...

    def teaching_recommendation(self, misconception: str) -> str:
        ...
```

All modules must:

1. Generate original syllabus-appropriate questions dynamically (not a fixed hardcoded question bank).
2. Validate every generated option or answer mathematically. Reject invalid questions.
3. Provide *one* correct option, and use incorrect options to test specific misconceptions.
4. Return `InternalQuestion` with a unique ID, statement, four options and the correct option ID.
5. NEVER send the correct option ID or misconception labels to students before submission.
6. Provide a useful correction and a teacher intervention linked to the selected misconception.
7. Provide automated tests for at least 100 generated variants per difficulty level.
8. Document unsupported question types (e.g. freehand geometry or handwritten solutions).

After completing a module, register it in `app/topics/__init__.py` and change its `ready` value to `True`.

> Important: In milestone one the wrong choices are diagnostic *signals*, not definitive evidence. More reliable adaptive diagnosis will require teacher-labelled student responses, additional questions and evaluation.
