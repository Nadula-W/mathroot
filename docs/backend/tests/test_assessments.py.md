# test_assessments.py — code explained

**Source:** [backend/tests/test_assessments.py](../../../backend/tests/test_assessments.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Exercises real FastAPI assessment routes with controlled users and a fake database: enrollment, permissions, scores, snapshots, retries and deletion.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–5: Code section

```python
"""Authenticated assessment workflow, using disposable in-memory records."""
from dataclasses import asdict
from app.topics.development.binomial.manual import BinomialTopic
from app.main import app
from app.supabase_auth import current_user
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 7–10: seed()

```python
def seed(client, count=3, test_id='test-one'):
    questions = [asdict(BinomialTopic().generate_question('easy')) for _ in range(count)]
    client.db.setdefault('mathroot_tests', []).append({'id': test_id, 'title': 'Binomial test', 'class_id': 'demo3', 'teacher_id': 'teacher', 'questions': questions})
    return questions
```

**Explanation:**

- Creates questions/records only in the test fixture's in-memory database.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 12–13: enroll()

```python
def enroll(client):
    return client.post('/api/classes/join', json={'class_id': 'demo3', 'join_code': 'secret-code'})
```

**Explanation:**

- Joins the disposable test class through the API to prepare an enrolled-user scenario.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 15–16: teacher()

```python
def teacher(client, id='teacher'):
    client.user.update(id=id, role='teacher', requested_role='teacher')
```

**Explanation:**

- Changes the controlled test identity to an approved teacher; this is a test helper, not a production approval endpoint.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 18–34: test_join_discovery_and_direct_link_authorization()

```python
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
```

**Explanation:**

- Tests that join discovery and direct link authorization. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 36–59: test_resume_scoring_duplicate_and_results()

```python
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
```

**Explanation:**

- Tests that resume scoring duplicate and results. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 60–62: test_resume_scoring_duplicate_and_results()

```python
    assert summary['students'][0]['full_name'] == 'Student Name'
    assert summary['topics_results'][0]['misconceptions']
    assert len(client.get('/api/tests/test-one/students/student').json()['answers']) == 3
```

**Explanation:**

- Tests that resume scoring duplicate and results. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 64–81: test_roles_ownership_and_deletion()

```python
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
```

**Explanation:**

- Tests that roles ownership and deletion. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 83–91: test_pending_teacher_and_missing_token()

```python
def test_pending_teacher_and_missing_token(client):
    seed(client)
    client.user['requested_role'] = 'teacher'
    assert enroll(client).status_code == 403
    assert client.get('/api/teacher/tests').status_code == 403
    app.dependency_overrides.pop(current_user)
    assert client.get('/api/student/classes').status_code == 401
    assert client.get('/api/tests/test-one').status_code == 401
    assert client.delete('/api/tests/test-one').status_code == 401
```

**Explanation:**

- Tests that pending teacher and missing token. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Replaces real authentication only inside tests. Clearing overrides restores normal application dependencies.

## Lines 93–97: test_invalid_question_and_option()

```python
def test_invalid_question_and_option(client):
    question = seed(client, 1)[0]; enroll(client)
    assert client.post('/api/tests/test-one/answers/submit', json={'question_id': 'missing', 'option_id': 'missing'}).status_code == 404
    assert client.post('/api/tests/test-one/answers/submit', json={'question_id': question['id'], 'option_id': 'missing'}).status_code == 422
    assert not client.db.get('mathroot_answers')
```

**Explanation:**

- Tests that invalid question and option. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 99–102: test_create_test_persists_and_uses_configured_generator()

```python
def test_create_test_persists_and_uses_configured_generator(client, monkeypatch):
    from app import assessments
    generator = BinomialTopic()
    calls = []
```

**Explanation:**

- Tests that create test persists and uses configured generator. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 103–103: Generator

```python
    class Generator:
```

**Explanation:**

- Groups the fields/methods of Generator. Declarations alone do not call a model or create database records; the following method sections explain execution.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 104–106: generate_question()

```python
        def generate_question(self, difficulty):
            calls.append(difficulty)
            return generator.generate_question(difficulty)
```

**Explanation:**

- In ai.py/manual.py this is an unfinished topic TODO. In generator.py it validates difficulty, tries AI plus mathematical validation, and falls back to the manual generator. The adapter class delegates to the same module-level function.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 107–117: test_create_test_persists_and_uses_configured_generator()

```python
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
```

**Explanation:**

- Tests that create test persists and uses configured generator. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 120–124: test_insert_race_returns_original_answer()

```python
def test_insert_race_returns_original_answer(client, monkeypatch):
    from conftest import Query
    question = seed(client, 1)[0]; enroll(client)
    original = Query.execute
    raced = False
```

**Explanation:**

- Tests that insert race returns original answer. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 125–131: execute()

```python
    def execute(query):
        nonlocal raced
        if query.name == 'mathroot_answers' and query.operation == 'insert' and not raced:
            raced = True
            original(query)  # The other request won the unique-key race.
            raise ValueError('duplicate key')
        return original(query)
```

**Explanation:**

- Defines execute with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 132–136: test_insert_race_returns_original_answer()

```python
    monkeypatch.setattr(Query, 'execute', execute)
    response = client.post('/api/tests/test-one/answers/submit', json={'question_id': question['id'], 'option_id': question['correct_option_id']})
    assert response.status_code == 200
    assert response.json()['correct']
    assert len(client.db['mathroot_answers']) == 1
```

**Explanation:**

- Tests that insert race returns original answer. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 139–148: test_other_student_cannot_read_private_results()

```python
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
```

**Explanation:**

- Tests that other student cannot read private results. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Connected files

Follow these imports to their matching code explanations:

- [app/main.py](../app/main.py.md)
- [app/supabase_auth.py](../app/supabase_auth.py.md)
- [app/topics/development/binomial/manual.py](../app/topics/development/binomial/manual.py.md)

## How to explain this file in the viva

“Exercises real FastAPI assessment routes with controlled users and a fake database: enrollment, permissions, scores, snapshots, retries and deletion.”
