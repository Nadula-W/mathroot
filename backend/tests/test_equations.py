"""Nimsara's isolated equation generation and fallback checks."""
from dataclasses import replace
from fractions import Fraction
import re

import pytest
from app.topics.development.equations import ai, generator, manual


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_generated_variants(difficulty):
    ids = set()
    for _ in range(100):
        question = manual.generate_question(difficulty)
        assert question.id not in ids
        ids.add(question.id)
        manual.validate_question(question)
        # Independently substitute each option into the original equation.
        numbers = list(map(int, re.findall(r'-?\d+', question.source_expression)))
        if difficulty == 'easy':
            a, b, d = numbers
            c = 0
        else:
            a, b, c, d = numbers
        for option in question.options:
            x = Fraction(option.text.removeprefix('x = '))
            left = a * (x + b) if difficulty == 'hard' else a * x + b
            assert (left == c * x + d) == (option.id == question.correct_option_id)
            assert manual.verify_answer(question, option.id) == (left == c * x + d)
            assert manual.feedback(question, option.misconception)
            assert manual.teaching_recommendation(option.misconception)


@pytest.mark.parametrize('field,value', [
    ('correct_option_id', 'missing'), ('correct_expression', '999'),
    ('statement', 'altered'), ('explanation', 'untrusted steps'),
    ('source_expression', '__import__("os")'),
    ('source_expression', '2*x + (1) = 2*x + (1)'),
])
def test_reject_tampered_questions(field, value):
    question = manual.generate_question('medium')
    with pytest.raises(ValueError):
        manual.validate_question(replace(question, **{field: value}))


def test_reject_duplicate_options_and_unknown_selection():
    question = manual.generate_question('easy')
    with pytest.raises(ValueError):
        manual.validate_question(replace(question, options=[question.options[0]] * 4))
    with pytest.raises(ValueError):
        manual.verify_answer(question, 'missing')


@pytest.mark.parametrize('error', [TimeoutError(), ValueError('Bad JSON'), RuntimeError('Missing credentials')])
def test_provider_failure_falls_back(monkeypatch, error):
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'auto')
    def fail(_):
        raise error
    monkeypatch.setattr(ai, 'generate_question', fail)
    manual.validate_question(generator.generate_question('hard'))


def test_invalid_provider_key_falls_back(monkeypatch):
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'auto')
    question = manual.generate_question('easy')
    monkeypatch.setattr(ai, 'generate_question', lambda _: replace(question, correct_option_id='wrong'))
    result = generator.generate_question('easy')
    assert result.id != question.id
    manual.validate_question(result)


def test_manual_mode_skips_provider(monkeypatch):
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'manual')
    def fail(_):
        pytest.fail('Manual mode contacted provider')
    monkeypatch.setattr(ai, 'generate_question', fail)
    manual.validate_question(generator.generate_question('easy'))
    with pytest.raises(ValueError):
        generator.generate_question('invalid')


def test_valid_provider_question_is_accepted(monkeypatch):
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'auto')
    question = manual.generate_question('medium')
    monkeypatch.setattr(ai, 'generate_question', lambda _: question)
    assert generator.generate_question('medium') is question


def test_shared_verifier_retains_grade_on_provider_failure(monkeypatch):
    from app.topics.development.equations.verifier import verify_answer
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'manual')
    question = manual.generate_question('easy')
    for option in question.options:
        result = verify_answer(question, option.id)
        assert result['correct'] == (option.id == question.correct_option_id)


@pytest.fixture
def ollama(monkeypatch):
    import httpx
    import json
    original = httpx.Client
    state = {'content': {'source_expression': '3*x + (4) = 19'}, 'status': 200}
    def handler(request):
        if state.get('timeout'):
            raise httpx.ReadTimeout('timeout', request=request)
        if 'raw' in state:
            return httpx.Response(state['status'], content=state['raw'])
        return httpx.Response(state['status'], json={'message': {'content': json.dumps(state['content'])}})
    monkeypatch.setattr(ai.httpx, 'Client', lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'auto')
    monkeypatch.setenv('MATHROOT_EQUATIONS_PROVIDER', 'ollama')
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODEL', 'test-model')
    return state


def test_real_adapter_generation(ollama):
    question = ai.generate_question('easy')
    assert question.correct_expression == '5'
    manual.validate_question(question)


@pytest.mark.parametrize('failure', ['timeout', 'json', 'schema', 'math', 'oversized', 'http'])
def test_real_adapter_fallback(ollama, failure):
    if failure == 'timeout':
        ollama['timeout'] = True
    elif failure == 'json':
        ollama['raw'] = b'not json'
    elif failure == 'schema':
        ollama['content'] = {'unexpected': True}
    elif failure == 'math':
        ollama['content'] = {'source_expression': '2*x + (1) = 2*x + (1)'}
    elif failure == 'oversized':
        ollama['raw'] = b'x' * 32001
    else:
        ollama['status'] = 503
    manual.validate_question(generator.generate_question('easy'))


def test_missing_model_skips_network(monkeypatch):
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'auto')
    monkeypatch.delenv('MATHROOT_EQUATIONS_MODEL', raising=False)
    monkeypatch.setattr(ai.httpx, 'Client', lambda **_: pytest.fail('Missing model contacted network'))
    manual.validate_question(generator.generate_question('easy'))


@pytest.mark.parametrize('value', ['nan', 'inf', '-1', '1000', 'bad'])
def test_timeout_is_bounded(monkeypatch, value):
    monkeypatch.setenv('MATHROOT_EQUATIONS_TIMEOUT_SECONDS', value)
    assert 0.1 <= ai.configuration()['timeout_seconds'] <= 4


@pytest.mark.parametrize('wrong_grade', [False, True])
def test_grounded_ai_analysis(ollama, monkeypatch, wrong_grade):
    from app.topics.development.equations.verifier import verify_answer
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto')
    question = manual.generate_question('easy')
    option = next(o for o in question.options if o.misconception)
    ollama['content'] = {
        'proposed_correct': wrong_grade,
        'explanation': manual.feedback(question, option.misconception),
        'suspected_misconception': option.misconception,
        'confidence': 0.95,
        'corrective_guidance': manual.teaching_recommendation(option.misconception),
    }
    result = verify_answer(question, option.id)
    assert result['correct'] is False
    assert result['verification_method'] == ('manual_fallback' if wrong_grade else 'ai_assisted')


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_bilingual_templates_preserve_math(difficulty):
    from app.presentation import mask_math
    topic = generator.EquationsTopic()
    question = manual.generate_question(difficulty)
    original = repr(question)
    texts = [question.statement, question.explanation, manual.feedback(question, None)]
    for code in manual.MISCONCEPTIONS:
        texts.extend([manual.feedback(question, code), manual.teaching_recommendation(code)])
    for text in texts:
        translated = topic.presentation_text('feedback', text, question)
        assert translated and any('\u0d80' <= ch <= '\u0dff' for ch in translated)
        assert mask_math(text)[1] == mask_math(translated)[1]
        assert topic.validate_translation('feedback', text, translated, question) is True
        assert topic.validate_translation('feedback', text, translated + ' 999', question) is False
        assert topic.validate_translation('feedback', text, 'අර්ථය වෙනස් කළ වාක්‍යයකි.', question) is False
    assert repr(question) == original
    assert topic.presentation_text('feedback', 'Unknown historical text', question) is None


def test_translation_adapter_and_guards(ollama):
    from app.presentation import restore_translation
    ollama['content'] = {'text': 'විසඳන්න: [[MATH_0]]'}
    provider = ai.TopicTranslationProvider()
    assert provider.translate('Solve: [[MATH_0]]') == ollama['content']['text']
    assert restore_translation(ollama['content']['text'], ['x = 5']) == 'විසඳන්න: x = 5'
    for text in ['විසඳන්න', '[[MATH_1]] [[MATH_0]]', 'විසඳන්න: [[MATH_0]] 99']:
        with pytest.raises(ValueError):
            restore_translation(text, ['x = 5'])
    ollama['content'] = {'text': 'විසඳන්න'}
    with pytest.raises(ValueError):
        provider.translate('Solve: [[MATH_0]]')
    ollama['timeout'] = True
    with pytest.raises(Exception):
        provider.translate('Solve: [[MATH_0]]')


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_equations_assessment_flow(client, monkeypatch, difficulty):
    from copy import deepcopy
    from test_assessments import teacher, enroll
    monkeypatch.setenv('MATHROOT_EQUATIONS_MODE', 'manual')
    teacher(client)
    created = client.post('/api/tests', json={
        'title': 'Equations test', 'class_id': 'demo3', 'topic_ids': ['equations'],
        'questions_per_topic': 2, 'difficulty': difficulty,
    })
    assert created.status_code == 200, created.text
    test_id = created.json()['test_id']
    stored = deepcopy(client.db['mathroot_tests'][-1])
    client.user.update(id='student', role='student', requested_role='student')
    enroll(client)
    public = client.get('/api/tests/' + test_id).json()
    assert client.db['mathroot_tests'][-1] == stored
    assert all(q['translations']['si']['statement'] for q in public['questions'])
    assert 'correct_option_id' not in str(public)
    assert 'misconception' not in str(public)
    assert 'explanation' not in str(public)
    for index, question in enumerate(stored['questions']):
        option = next(o for o in question['options'] if (o['misconception'] is None) == (index == 0))
        result = client.post('/api/tests/' + test_id + '/answers/submit', json={
            'question_id': question['id'], 'option_id': option['id'],
        })
        assert result.status_code == 200, result.text
        detail = result.json()
        assert detail['correct'] == (index == 0)
        assert not detail['translation_warnings']
        for field in ('statement', 'explanation', 'feedback', 'corrective_guidance', 'teaching_recommendation'):
            assert detail['translations']['si'][field]
    progress = client.get('/api/tests/' + test_id + '/progress').json()
    assert progress['correct'] == 1
    assert progress['percentage'] == 50
    teacher(client)
    report = client.get('/api/tests/' + test_id + '/results').json()
    assert report['topics_results'][0]['misconceptions'][0]['translations']['si']['recommendation']
