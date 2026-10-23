import json
from dataclasses import replace

import httpx
import pytest

from app.answer_verification import Analysis, OllamaFeedbackProvider, verify_answer
from app.topics.development.binomial.manual import BinomialTopic
from app.safe_symbolic import equivalent, parse_math


class GroundedProvider:
    def __init__(self, **changes):
        self.changes = changes
        self.calls = 0

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


@pytest.fixture
def topic():
    return BinomialTopic()


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


@pytest.mark.parametrize('error', [httpx.ConnectError('offline'), httpx.ReadTimeout('timeout'), ValueError('bad json'), RuntimeError('unexpected')])
def test_provider_failure_is_automatic(monkeypatch, topic, error):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    class Failure:
        def analyze(self, context): raise error
    q = topic.generate_question('medium')
    wrong = next(o for o in q.options if o.misconception == 'SIGN_ERROR')
    result = verify_answer(q, wrong.id, topic, Failure())
    assert not result['correct']
    assert result['verification_method'] == 'manual_fallback'
    assert result['suspected_misconception'] == 'SIGN_ERROR'


def test_manual_does_not_call_ai(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'manual')
    provider = GroundedProvider()
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic, provider)['verification_method'] == 'manual_fallback'
    assert provider.calls == 0


def test_topic_can_choose_its_own_provider(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    provider = GroundedProvider()
    monkeypatch.setattr(topic, 'answer_feedback_provider', lambda: provider, raising=False)
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic)['verification_method'] == 'ai_assisted'
    assert provider.calls == 1


def test_topic_provider_configuration_failure_uses_manual(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    def unavailable():
        raise ValueError('Missing topic provider configuration')
    monkeypatch.setattr(topic, 'answer_feedback_provider', unavailable, raising=False)
    q = topic.generate_question('easy')
    result = verify_answer(q, q.correct_option_id, topic)
    assert result['correct']
    assert result['verification_method'] == 'manual_fallback'


def test_unknown_distractor_never_gets_correct_feedback(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'manual')
    q = topic.generate_question('easy')
    wrong = next(o for o in q.options if o.misconception)
    q = replace(q, options=[replace(o, misconception=None) if o.id == wrong.id else o for o in q.options])
    result = verify_answer(q, wrong.id, topic)
    assert not result['correct'] and result['suspected_misconception'] is None
    assert result['feedback'].startswith('Incorrect')


@pytest.mark.parametrize('content', ['not json', '{}', '{"proposed_correct":"true"}'])
def test_real_adapter_validates_ollama_json(monkeypatch, topic, content):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    def post(self, url, **kwargs):
        assert kwargs['json']['format']['type'] == 'object'
        return httpx.Response(200, request=httpx.Request('POST', url), json={'message': {'content': content}})
    monkeypatch.setattr(httpx.Client, 'post', post)
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic)['verification_method'] == 'manual_fallback'


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


@pytest.mark.parametrize('bad', ["__import__('os')", 'x.__class__', 'sin(x)', 'y+1', 'x**100000', '1/0', 'True', 'x**x', '(x+1)**6**6'])
def test_symbolic_rejects_untrusted_syntax(bad):
    with pytest.raises((ValueError, SyntaxError)):
        parse_math(bad)


def test_safe_symbolic_equivalence():
    assert equivalent('3*(x+4)', '3*x+12')
    assert not equivalent('3*x+4', '3*x+12')


@pytest.mark.parametrize('correct', [True, False])
def test_ollama_http_adapter_success(monkeypatch, topic, correct):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    q = topic.generate_question('medium')
    option = next(o for o in q.options if (o.id == q.correct_option_id) == correct)
    def post(self, url, **kwargs):
        context = json.loads(kwargs['json']['messages'][1]['content'])
        assert context['verified_correct'] == correct
        assert 'student_id' not in context
        selection = {'proposed_correct': correct, 'explanation_index': 0,
                     'suspected_misconception': option.misconception, 'confidence': 0.93, 'guidance_index': 0}
        return httpx.Response(200, request=httpx.Request('POST', url), json={'message': {'content': json.dumps(selection)}})
    monkeypatch.setattr(httpx.Client, 'post', post)
    result = verify_answer(q, option.id, topic)
    assert result['correct'] == correct
    assert result['verification_method'] == 'ai_assisted'


def test_ollama_model_unavailable(monkeypatch, topic):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    def post(self, url, **kwargs):
        return httpx.Response(404, request=httpx.Request('POST', url), json={'error': 'model not found'})
    monkeypatch.setattr(httpx.Client, 'post', post)
    q = topic.generate_question('easy')
    assert verify_answer(q, q.correct_option_id, topic)['verification_method'] == 'manual_fallback'
