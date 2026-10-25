"""Bilingual presentation exercises the existing routes with an in-memory DB."""
from copy import deepcopy

import pytest

from test_assessments import seed, enroll, teacher
from test_answer_verification import GroundedProvider


def test_both_wordings_keep_question_and_option_identities(client):
    questions = seed(client, 3)
    enroll(client)
    before = deepcopy(client.db)
    first = client.get('/api/tests/test-one').json()
    again = client.get('/api/tests/test-one').json()
    assert first == again
    for original, public in zip(questions, first['questions']):
        assert public['question_id'] == original['id']
        assert [o['id'] for o in public['options']] == [o['id'] for o in original['options']]
        assert [o['text'] for o in public['options']] == [o['text'] for o in original['options']]
        expression = original['statement'].split(': ', 1)[1]
        assert public['translations']['si']['statement'] == 'ප්‍රසාරණය කර සුළු කරන්න: ' + expression
        assert not public['translation_warnings']
        assert 'correct_option_id' not in str(public)
        assert 'explanation' not in str(public)
        assert 'misconception' not in str(public)
    assert client.db == before


@pytest.mark.parametrize('ai', [False, True])
def test_saved_feedback_is_bilingual_without_changing_grade_or_snapshot(client, monkeypatch, ai):
    from app import answer_verification
    question = seed(client, 1)[0]
    enroll(client)
    provider = GroundedProvider()
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto' if ai else 'manual')
    monkeypatch.setattr(answer_verification, 'OllamaFeedbackProvider', lambda: provider)
    wrong = next(o for o in question['options'] if o['misconception'] == 'SIGN_ERROR')
    result = client.post('/api/tests/test-one/answers/submit', json={
        'question_id': question['id'], 'option_id': wrong['id'],
    }).json()
    assert result['correct'] is False
    assert result['verification_method'] == ('ai_assisted' if ai else 'manual_fallback')
    for field in ('statement', 'feedback', 'explanation', 'corrective_guidance', 'teaching_recommendation'):
        assert result['translations']['si'][field]
    assert not result['translation_warnings']
    row = deepcopy(client.db['mathroot_answers'][0])
    assert 'translations' not in row['verification']
    assert row['verification']['feedback'] == result['feedback']
    progress = client.get('/api/tests/test-one/progress').json()
    assert progress['correct'] == 0 and progress['percentage'] == 0
    assert progress['status'] == 'Completed'
    assert progress['answers'][0]['translations'] == result['translations']
    assert client.db['mathroot_answers'][0] == row
    assert provider.calls == int(ai)

    teacher(client)
    report = client.get('/api/tests/test-one/results').json()
    signal = report['topics_results'][0]['misconceptions'][0]
    assert signal['code'] == 'SIGN_ERROR'
    assert signal['translations']['si']['recommendation']
    assert report['average_score'] == 0
    assert client.get('/api/tests/test-one/students/student').json()['answers'][0]['translations'] == result['translations']


def test_historical_questions_and_answers_without_snapshots_still_translate(client):
    question = seed(client, 1)[0]
    enroll(client)
    client.post('/api/tests/test-one/answers/submit', json={
        'question_id': question['id'], 'option_id': question['correct_option_id'],
    })
    client.db['mathroot_answers'][0].pop('verification')
    before = deepcopy(client.db)
    result = client.get('/api/tests/test-one/progress').json()
    assert result['correct'] == 1 and result['percentage'] == 100
    answer = result['answers'][0]
    assert answer['translations']['si']['statement']
    assert answer['translations']['si']['feedback']
    assert answer['translations']['si']['explanation']
    assert not answer['translation_warnings']
    assert client.db == before


def test_unrecognized_historical_text_is_retained_and_reported(client):
    question = seed(client, 1)[0]
    question['statement'] = 'A custom historical question with unknown wording.'
    enroll(client)
    response = client.get('/api/tests/test-one').json()['questions'][0]
    assert response['statement'] == question['statement']
    assert 'statement' in response['translation_warnings']
    assert 'statement' not in response['translations']['si']


def test_untranslated_worded_option_has_its_own_warning(client):
    question = seed(client, 1)[0]
    question['options'][0]['text'] = 'An unfamiliar verbal answer'
    enroll(client)
    response = client.get('/api/tests/test-one').json()['questions'][0]
    option = response['options'][0]
    assert option['id'] == question['options'][0]['id']
    assert option['text'] == 'An unfamiliar verbal answer'
    assert option['translation_warnings'] == ['text']
    assert f"options.{option['id']}.text" in response['translation_warnings']


def test_bilingual_manual_test_creation_and_topic_readiness(client, monkeypatch):
    monkeypatch.setenv('MATHROOT_GENERATOR', 'manual')
    teacher(client)
    created = client.post('/api/tests', json={
        'title': 'Bilingual test', 'class_id': 'demo3', 'topic_ids': ['binomial'],
        'questions_per_topic': 2, 'difficulty': 'medium',
    })
    assert created.status_code == 200
    test_id = created.json()['test_id']
    stored = deepcopy(client.db['mathroot_tests'][-1])
    client.user.update(id='student', role='student', requested_role='student')
    enroll(client)
    public = client.get('/api/tests/' + test_id).json()
    assert all(q['translations']['si']['statement'] for q in public['questions'])
    assert client.db['mathroot_tests'][-1] == stored
    topics = client.get('/api/topics').json()
    assert [t['id'] for t in topics if t['ready']] == ['binomial', 'algebraic_fractions']
