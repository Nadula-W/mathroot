import random
from sympy import Symbol, simplify, sympify
from app.topics.binomial import BinomialTopic
from app import storage

x = Symbol('x')


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


def test_question_generation_hides_answer(client):
    result = client.post('/api/questions/generate', json={'topic_id': 'binomial', 'difficulty': 'easy', 'class_id': 'class-A'})
    assert result.status_code == 200
    question = result.json()
    assert len(question['options']) == 4
    assert 'correct_option_id' not in question
    assert 'misconception' not in str(question['options'])
    assert all(len(o['id']) == 36 for o in question['options'])


def test_wrong_answer_and_teacher_summary(client):
    q = client.post('/api/questions/generate', json={'topic_id': 'binomial', 'class_id': 'class-B'}).json()
    internal = storage.get_question(q['question_id'])[0]
    wrong_id = next(o.id for o in internal.options if o.misconception == 'DISTRIBUTION_CONSTANT')
    result = client.post('/api/answers/submit', json={
        'question_id': q['question_id'], 'option_id': wrong_id, 'student_id': 'S001'
    })
    assert result.status_code == 200
    assert not result.json()['correct']
    assert result.json()['suspected_misconception'] == 'DISTRIBUTION_CONSTANT'
    assert result.json()['diagnosis_status'] == 'suspected'
    summary = client.get('/api/teacher/summary', params={'class_id': 'class-B'}).json()
    assert summary['total_answers'] == 1
    assert summary['students'] == 1
    assert summary['misconception_counts'][0]['code'] == 'DISTRIBUTION_CONSTANT'
    assert len(summary['recommendations']) == 1
    duplicate = client.post('/api/answers/submit', json={
        'question_id': q['question_id'], 'option_id': wrong_id, 'student_id': 'S001'
    })
    assert duplicate.status_code == 409


def test_adaptive_next_and_repeated_evidence(client):
    generated = client.post('/api/practice/next', json={
        'topic_id': 'binomial', 'class_id': 'class-C', 'student_id': 'S002'
    }).json()
    assert generated['difficulty'] == 'easy'
    for iteration in range(2):
        internal = storage.get_question(generated['question_id'])[0]
        wrong_id = next(o.id for o in internal.options if o.misconception == 'DISTRIBUTION_CONSTANT')
        resp = client.post('/api/answers/submit', json={
            'question_id': generated['question_id'], 'student_id': 'S002',
            'option_id': wrong_id,
        })
        assert resp.status_code == 200
        assert resp.json()['diagnosis_status'] == ('suspected' if iteration == 0 else 'repeated_signal')
        generated = client.post('/api/practice/next', json={
            'topic_id': 'binomial', 'class_id': 'class-C', 'student_id': 'S002'
        }).json()


def test_topic_ownership(client):
    topics = client.get('/api/topics').json()
    assert len(topics) == 5
    assert sum(item['ready'] for item in topics) == 1
    assert client.post('/api/questions/generate', json={'topic_id': 'equations'}).status_code == 422
