# Common contract for every topic owner

The following module ownership has already been agreed:

| Owner | Module | Topic ID |
|---|---|---|
| Nadula | `app/topics/development/binomial/manual.py` | `binomial` |
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

## Optional grounded answer feedback

The existing TopicModule methods and InternalQuestion contract are unchanged. `app.answer_verification.verify_answer(question, option_id, topic, provider=None)` is shared across topics. It always grades MCQs by comparing the submitted ID with the stored correct option ID. A topic may optionally supply:

```python
misconception_definitions = {"STABLE_CODE": "Description of the error evidence"}

def verification_feedback(self, question, misconception, correct):
    # Return additional trusted explanation and corrective-guidance strings.
    # Mathematical steps must be independently validated by the topic.
    return ["Possible misconception: ... " + question.explanation], ["Learning tip ..."]
```

Ollama selects among these grounded explanations and corrections, returns its proposed grade, supported misconception and confidence, and is accepted only if all checks agree with the deterministic evidence. It cannot introduce a new diagnosis or arbitrary mathematical expression. A topic without the optional hook works with its existing feedback and recommendation. Unknown distractors produce an uncertain diagnosis, never a fabricated misconception or a false Correct message.

Binomial definitions also reserve COEFFICIENT_ERROR, UNLIKE_TERMS, ARITHMETIC_ERROR and VARIABLE_CONSTANT_CONFUSION for future evidence-bearing question variants. The current generator's three distractors establish only DISTRIBUTION_CONSTANT, DISTRIBUTION_VARIABLE and SIGN_ERROR. Do not infer the additional categories solely from a single existing selection.

To integrate another provider, implement FeedbackProvider.analyze(context) -> Analysis and select it in the backend composition. Context contains only question content and approved feedback; never add user identity, secrets or session tokens. Pages and submission contracts do not change.

For future free-text adapters, `app.safe_symbolic` provides a bounded AST parser and SymPy equivalence check for explicit arithmetic such as `3*(x+4)`. It never evaluates Python or calls sympify on student strings. It rejects functions, attributes, unknown variables, excessive sizes and exponents. It checks algebraic equality on the common domain; topic adapters must additionally enforce domain restrictions and question-specific rules. Free-text submission is not enabled by this change.
