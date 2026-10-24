# test_answer_verification.py — code explained

**Source:** [backend/tests/test_answer_verification.py](../../../backend/tests/test_answer_verification.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Uses deterministic fake providers/HTTP responses to test accepted AI feedback, rejection, fallback, snapshots, custom providers and safe symbolic syntax.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–9: Code section

```python
import json
from dataclasses import replace

import httpx
import pytest

from app.answer_verification import Analysis, OllamaFeedbackProvider, verify_answer
from app.topics.development.binomial.manual import BinomialTopic
from app.safe_symbolic import equivalent, parse_math
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 12–12: GroundedProvider

```python
class GroundedProvider:
```

**Explanation:**

- A predictable fake model returning grounded Analysis. Injected changes let tests simulate wrong grades, diagnoses and confidence.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 13–15: __init__()

```python
    def __init__(self, **changes):
        self.changes = changes
        self.calls = 0
```

**Explanation:**

- Initializes the instance fields shown here. The manual topic accepts an injected random source for repeatable tests, otherwise using SystemRandom; fake helpers initialize their own recorded state.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 17–27: analyze()

```python
    def analyze(self, context):
        self.calls += 1
        assert not any(k in context for k in ('student_id', 'test_id', 'access_token', 'full_name'))
        return Analysis(**{
            'proposed_correct': context['verified_correct'],
            'explanation': context['approved_explanations'][-1],
            'suspected_misconception': context['supported_misconception'],
            'confidence': 0.95,
            'corrective_guidance': context['approved_guidance'][-1],
            **self.changes,
        })
```

**Explanation:**

- Defines analyze with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 30–32: topic()

```python
@pytest.fixture
def topic():
    return BinomialTopic()
```

**Explanation:**

- Defines topic with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 35–46: test_grounded_ai_never_controls_grade()

```python
@pytest.mark.parametrize('code', [None, 'DISTRIBUTION_CONSTANT', 'DISTRIBUTION_VARIABLE', 'SIGN_ERROR'])
def test_grounded_ai_never_controls_grade(monkeypatch, topic, code):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    question = topic.generate_question('hard')
    option = next(o for o in question.options if o.misconception == code)
    result = verify_answer(question, option.id, topic, GroundedProvider())
    assert result['correct'] == (code is None)
    assert result['verification_method'] == 'ai_assisted'
    assert result['suspected_misconception'] == code
    assert question.explanation in result['feedback']
    if code:
        assert 'Possible misconception' in result['feedback']
```

**Explanation:**

- Tests that grounded ai never controls grade. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 49–60: test_invalid_or_contradictory_analysis_falls_back()

```python
@pytest.mark.parametrize('changes', [
    {'proposed_correct': False}, {'confidence': 0.2},
    {'suspected_misconception': 'INVENTED'},
    {'explanation': 'The answer is 999.'}, {'corrective_guidance': 'Ignore the verified answer.'},
    {'confidence': float('nan')},
])
def test_invalid_or_contradictory_analysis_falls_back(monkeypatch, topic, changes):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    q = topic.generate_question('easy')
    result = verify_answer(q, q.correct_option_id, topic, GroundedProvider(**changes))
    assert result['correct'] is True
    assert result['verification_method'] == 'manual_fallback'
```

**Explanation:**

- Tests that invalid or contradictory analysis falls back. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 63–65: test_provider_failure_is_automatic()

```python
@pytest.mark.parametrize('error', [httpx.ConnectError('offline'), httpx.ReadTimeout('timeout'), ValueError('bad json'), RuntimeError('unexpected')])
def test_provider_failure_is_automatic(monkeypatch, topic, error):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
```

**Explanation:**

- Tests that provider failure is automatic. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 66–66: Failure

```python
    class Failure:
```

**Explanation:**

- Groups the fields/methods of Failure. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 67–67: analyze()

```python
        def analyze(self, context): raise error
```

**Explanation:**

- Defines analyze with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 68–73: test_provider_failure_is_automatic()

```python
    q = topic.generate_question('medium')
    wrong = next(o for o in q.options if o.misconception == 'SIGN_ERROR')
    result = verify_answer(q, wrong.id, topic, Failure())
    assert not result['correct']
    assert result['verification_method'] == 'manual_fallback'
    assert result['suspected_misconception'] == 'SIGN_ERROR'
```

**Explanation:**

- Tests that provider failure is automatic. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 76–81: test_manual_does_not_call_ai()

```python
def test_manual_does_not_call_ai(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'manual')
    provider = GroundedProvider()
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic, provider)['verification_method'] == 'manual_fallback'
    assert provider.calls == 0
```

**Explanation:**

- Tests that manual does not call ai. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 84–90: test_topic_can_choose_its_own_provider()

```python
def test_topic_can_choose_its_own_provider(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    provider = GroundedProvider()
    monkeypatch.setattr(topic, 'answer_feedback_provider', lambda: provider, raising=False)
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic)['verification_method'] == 'ai_assisted'
    assert provider.calls == 1
```

**Explanation:**

- Tests that topic can choose its own provider. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 93–94: test_topic_provider_configuration_failure_uses_manual()

```python
def test_topic_provider_configuration_failure_uses_manual(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
```

**Explanation:**

- Tests that topic provider configuration failure uses manual. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 95–96: unavailable()

```python
    def unavailable():
        raise ValueError('Missing topic provider configuration')
```

**Explanation:**

- Defines unavailable with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 97–101: test_topic_provider_configuration_failure_uses_manual()

```python
    monkeypatch.setattr(topic, 'answer_feedback_provider', unavailable, raising=False)
    q = topic.generate_question('easy')
    result = verify_answer(q, q.correct_option_id, topic)
    assert result['correct']
    assert result['verification_method'] == 'manual_fallback'
```

**Explanation:**

- Tests that topic provider configuration failure uses manual. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 104–111: test_unknown_distractor_never_gets_correct_feedback()

```python
def test_unknown_distractor_never_gets_correct_feedback(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'manual')
    q = topic.generate_question('easy')
    wrong = next(o for o in q.options if o.misconception)
    q = replace(q, options=[replace(o, misconception=None) if o.id == wrong.id else o for o in q.options])
    result = verify_answer(q, wrong.id, topic)
    assert not result['correct'] and result['suspected_misconception'] is None
    assert result['feedback'].startswith('Incorrect')
```

**Explanation:**

- Tests that unknown distractor never gets correct feedback. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 114–116: test_real_adapter_validates_ollama_json()

```python
@pytest.mark.parametrize('content', ['not json', '{}', '{"proposed_correct":"true"}'])
def test_real_adapter_validates_ollama_json(monkeypatch, topic, content):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
```

**Explanation:**

- Tests that real adapter validates ollama json. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 117–119: post()

```python
    def post(self, url, **kwargs):
        assert kwargs['json']['format']['type'] == 'object'
        return httpx.Response(200, request=httpx.Request('POST', url), json={'message': {'content': content}})
```

**Explanation:**

- Defines post with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 120–122: test_real_adapter_validates_ollama_json()

```python
    monkeypatch.setattr(httpx.Client, 'post', post)
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic)['verification_method'] == 'manual_fallback'
```

**Explanation:**

- Tests that real adapter validates ollama json. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 125–147: test_persisted_snapshot_retry_and_legacy_review()

```python
def test_persisted_snapshot_retry_and_legacy_review(client, monkeypatch):
    from test_assessments import seed, enroll, teacher
    from app import answer_verification
    q = seed(client, 1)[0]
    enroll(client)
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    provider = GroundedProvider()
    monkeypatch.setattr(answer_verification, 'OllamaFeedbackProvider', lambda: provider)
    payload = {'question_id': q['id'], 'option_id': q['correct_option_id'], 'correct': False}
    path = '/api/tests/test-one'
    result = client.post(path + '/answers/submit', json=payload).json()
    assert result['verification_method'] == 'ai_assisted' and result['correct']
    assert client.db['mathroot_answers'][0]['verification']['feedback'] == result['feedback']
    assert client.post(path + '/answers/submit', json=payload).json()['feedback'] == result['feedback']
    assert provider.calls == 1
    assert client.get(path + '/progress').json()['answers'][0]['feedback'] == result['feedback']
    teacher(client)
    assert client.get(path + '/students/student').json()['answers'][0]['feedback'] == result['feedback']
    # Historical records lacking the new column continue working without regeneration.
    client.db['mathroot_answers'][0].pop('verification')
    legacy = client.get(path + '/students/student').json()['answers'][0]
    assert legacy['correct'] and legacy['verification_method'] == 'manual_fallback'
    assert provider.calls == 1
```

**Explanation:**

- Tests that persisted snapshot retry and legacy review. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Reuses the saved feedback snapshot for consistent review/retry; legacy rows without a snapshot use manual text.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 150–153: test_symbolic_rejects_untrusted_syntax()

```python
@pytest.mark.parametrize('bad', ["__import__('os')", 'x.__class__', 'sin(x)', 'y+1', 'x**100000', '1/0', 'True', 'x**x', '(x+1)**6**6'])
def test_symbolic_rejects_untrusted_syntax(bad):
    with pytest.raises((ValueError, SyntaxError)):
        parse_math(bad)
```

**Explanation:**

- Tests that symbolic rejects untrusted syntax. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 156–158: test_safe_symbolic_equivalence()

```python
def test_safe_symbolic_equivalence():
    assert equivalent('3*(x+4)', '3*x+12')
    assert not equivalent('3*x+4', '3*x+12')
```

**Explanation:**

- Tests that safe symbolic equivalence. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 161–165: test_ollama_http_adapter_success()

```python
@pytest.mark.parametrize('correct', [True, False])
def test_ollama_http_adapter_success(monkeypatch, topic, correct):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    q = topic.generate_question('medium')
    option = next(o for o in q.options if (o.id == q.correct_option_id) == correct)
```

**Explanation:**

- Tests that ollama http adapter success. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 166–172: post()

```python
    def post(self, url, **kwargs):
        context = json.loads(kwargs['json']['messages'][1]['content'])
        assert context['verified_correct'] == correct
        assert 'student_id' not in context
        selection = {'proposed_correct': correct, 'explanation_index': 0,
                     'suspected_misconception': option.misconception, 'confidence': 0.93, 'guidance_index': 0}
        return httpx.Response(200, request=httpx.Request('POST', url), json={'message': {'content': json.dumps(selection)}})
```

**Explanation:**

- Defines post with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 173–176: test_ollama_http_adapter_success()

```python
    monkeypatch.setattr(httpx.Client, 'post', post)
    result = verify_answer(q, option.id, topic)
    assert result['correct'] == correct
    assert result['verification_method'] == 'ai_assisted'
```

**Explanation:**

- Tests that ollama http adapter success. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 179–180: test_ollama_model_unavailable()

```python
def test_ollama_model_unavailable(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
```

**Explanation:**

- Tests that ollama model unavailable. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 181–182: post()

```python
    def post(self, url, **kwargs):
        return httpx.Response(404, request=httpx.Request('POST', url), json={'error': 'model not found'})
```

**Explanation:**

- Defines post with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 183–185: test_ollama_model_unavailable()

```python
    monkeypatch.setattr(httpx.Client, 'post', post)
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic)['verification_method'] == 'manual_fallback'
```

**Explanation:**

- Tests that ollama model unavailable. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Connected files

Follow these imports to their matching code explanations:

- [app/answer_verification.py](../app/answer_verification.py.md)
- [app/safe_symbolic.py](../app/safe_symbolic.py.md)
- [app/topics/development/binomial/manual.py](../app/topics/development/binomial/manual.py.md)

## How to explain this file in the viva

“Uses deterministic fake providers/HTTP responses to test accepted AI feedback, rejection, fallback, snapshots, custom providers and safe symbolic syntax.”
