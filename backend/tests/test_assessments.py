"""Authenticated assessment workflow, using disposable in-memory records."""
from dataclasses import asdict
from app.topics.binomial import BinomialTopic
from app.main import app
from app.supabase_auth import current_user

def seed(client, count=3, test_id='test-one'):
    questions = [asdict(BinomialTopic().generate_question('easy')) for _ in range(count)]
    client.db.setdefault('mathroot_tests', []).append({'id': test_id, 'title': 'Binomial test', 'class_id': 'demo3', 'teacher_id': 'teacher', 'questions': questions})
    return questions

def enroll(client):
    return client.post('/api/classes/join', json={'class_id': 'demo3', 'join_code': 'secret-code'})

def teacher(client, id='teacher'):
    client.user.update(id=id, role='teacher', requested_role='teacher')

def test_join_discovery_and_direct_link_authorization(client):
    seed(client)
    assert client.get('/api/student/classes').json() == []
    assert client.get('/api/tests?class_id=demo3').status_code == 403
    assert client.get('/api/tests/test-one').status_code == 403
    assert client.get('/api/tests/test-one/progress').status_code == 403
    assert client.post('/api/classes/join', json={'class_id': 'demo3', 'join_code': 'wrong-code'}).status_code == 403
    assert client.post('/api/classes/join', json={'class_id': 'missing', 'join_code': 'secret-code'}).status_code == 404
    assert enroll(client).json()['status'] == 'joined'
    assert enroll(client).json()['status'] == 'already_enrolled'
    assert len(client.db['mathroot_class_members']) == 1
    assert client.get('/api/student/classes').json()[0]['class_id'] == 'demo3'
    assert len(client.get('/api/tests?class_id=demo3').json()) == 1
    public = client.get('/api/tests/test-one').json()
    assert 'correct_option_id' not in str(public)
    assert 'misconception' not in str(public)
    assert client.get('/api/tests/test-one/progress').json()['answers'] == []

def test_resume_scoring_duplicate_and_results(client):
    questions = seed(client); enroll(client)
    for index, question in enumerate(questions):
        option = question['correct_option_id'] if index != 1 else next(o['id'] for o in question['options'] if o['id'] != question['correct_option_id'])
        payload = {'question_id': question['id'], 'option_id': option, 'student_id': 'forged-user'}
        response = client.post('/api/tests/test-one/answers/submit', json=payload)
        assert response.status_code == 200
        assert 'correct_answer' in response.json()
        # A retry with a different selection must return the original persisted answer.
        payload['option_id'] = next(o['id'] for o in question['options'] if o['id'] != option)
        duplicate = client.post('/api/tests/test-one/answers/submit', json=payload)
        assert duplicate.status_code == 200
        assert duplicate.json()['selected_option'] == response.json()['selected_option']
        saved = client.get('/api/tests/test-one/progress').json()
        assert len(saved['answers']) == index + 1
        assert saved['status'] == ('Completed' if index == 2 else 'In Progress')
        assert len(saved['answers']) == len(client.db['mathroot_answers'])
    assert {r['student_id'] for r in client.db['mathroot_answers']} == {'student'}
    assert saved['correct'] == 2 and saved['incorrect'] == 1 and saved['percentage'] == 66.7
    assert len(client.get('/api/student/results').json()) == 1
    teacher(client)
    summary = client.get('/api/tests/test-one/results').json()
    assert summary['completed_count'] == 1 and summary['enrolled_count'] == 1
    assert summary['average_score'] == 66.7
    assert summary['students'][0]['full_name'] == 'Student Name'
    assert summary['topics_results'][0]['misconceptions']
    assert len(client.get('/api/tests/test-one/students/student').json()['answers']) == 3

def test_roles_ownership_and_deletion(client):
    q = seed(client, 1)[0]; seed(client, 1, 'keep-me'); enroll(client)
    client.post('/api/tests/test-one/answers/submit', json={'question_id': q['id'], 'option_id': q['correct_option_id']})
    for path in ['/api/teacher/tests', '/api/tests/test-one/results', '/api/tests/test-one/students/student']:
        assert client.get(path).status_code == 403
    assert client.delete('/api/tests/test-one').status_code == 403
    teacher(client, 'other-teacher')
    assert client.get('/api/tests/test-one/results').status_code == 403
    assert client.get('/api/tests/test-one/students/student').status_code == 403
    assert client.delete('/api/tests/test-one').status_code == 403
    teacher(client)
    assert len(client.get('/api/teacher/tests').json()) == 2
    assert client.delete('/api/tests/test-one').status_code == 200
    assert [r['id'] for r in client.db['mathroot_tests']] == ['keep-me']
    assert client.db['mathroot_answers'] == []
    assert len(client.db['mathroot_classes']) == 1
    assert len(client.db['mathroot_class_members']) == 1
    assert client.get('/api/tests/test-one').status_code == 404

def test_pending_teacher_and_missing_token(client):
    seed(client)
    client.user['requested_role'] = 'teacher'
    assert enroll(client).status_code == 403
    assert client.get('/api/teacher/tests').status_code == 403
    app.dependency_overrides.pop(current_user)
    assert client.get('/api/student/classes').status_code == 401
    assert client.get('/api/tests/test-one').status_code == 401
    assert client.delete('/api/tests/test-one').status_code == 401

def test_invalid_question_and_option(client):
    question = seed(client, 1)[0]; enroll(client)
    assert client.post('/api/tests/test-one/answers/submit', json={'question_id': 'missing', 'option_id': 'missing'}).status_code == 404
    assert client.post('/api/tests/test-one/answers/submit', json={'question_id': question['id'], 'option_id': 'missing'}).status_code == 422
    assert not client.db.get('mathroot_answers')

def test_create_test_persists_and_uses_configured_generator(client, monkeypatch):
    from app import assessments
    generator = BinomialTopic()
    calls = []
    class Generator:
        def generate_question(self, difficulty):
            calls.append(difficulty)
            return generator.generate_question(difficulty)
    monkeypatch.setitem(assessments.TOPICS, 'binomial', Generator())
    teacher(client)
    response = client.post('/api/tests', json={'title': 'Three questions', 'class_id': 'demo3', 'topic_ids': ['binomial'], 'questions_per_topic': 3, 'difficulty': 'medium'})
    assert response.status_code == 200
    assert calls == ['medium'] * 3
    assert response.json()['question_count'] == 3
    assert len(client.db['mathroot_tests'][0]['questions']) == 3
    assert 'correct_option_id' not in str(response.json())
    client.user.update(id='student', role='student', requested_role='student')
    enroll(client)
    assert client.get('/api/tests?class_id=demo3').json()[0]['test_id'] == response.json()['test_id']


def test_insert_race_returns_original_answer(client, monkeypatch):
    from conftest import Query
    question = seed(client, 1)[0]; enroll(client)
    original = Query.execute
    raced = False
    def execute(query):
        nonlocal raced
        if query.name == 'mathroot_answers' and query.operation == 'insert' and not raced:
            raced = True
            original(query)  # The other request won the unique-key race.
            raise ValueError('duplicate key')
        return original(query)
    monkeypatch.setattr(Query, 'execute', execute)
    response = client.post('/api/tests/test-one/answers/submit', json={'question_id': question['id'], 'option_id': question['correct_option_id']})
    assert response.status_code == 200
    assert response.json()['correct']
    assert len(client.db['mathroot_answers']) == 1


def test_other_student_cannot_read_private_results(client):
    question = seed(client, 1)[0]; enroll(client)
    client.post('/api/tests/test-one/answers/submit', json={'question_id': question['id'], 'option_id': question['correct_option_id']})
    client.user['id'] = 'second-student'
    assert client.get('/api/tests/test-one/progress').status_code == 403
    assert client.get('/api/tests/test-one/students/student').status_code == 403
    enroll(client)
    own = client.get('/api/tests/test-one/progress').json()
    assert own['answers'] == [] and own['correct'] == 0
    assert client.get('/api/student/results').json() == []
