# verify_assessments.py — code explained

**Source:** [backend/scripts/verify_assessments.py](../../../backend/scripts/verify_assessments.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Optional live workflow check using its own disposable accounts/class/tests. It checks Auth, persistence, results and deletion, then cleans up its own records.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–13: Code section

```python
"""Opt-in live assessment smoke test. Creates and cleans up only its own records.
Run from backend: .venv/Scripts/python.exe scripts/verify_assessments.py
No existing classes, users, tests or answers are modified.
"""
import sys
from pathlib import Path
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from supabase import create_client
from app.main import app
from app.supabase_auth import admin_client
import os
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 16–20: main()

```python
def main():
    admin = admin_client()
    suffix = uuid4().hex
    class_id = f'codex-check-{suffix[:12]}'
    users, clients = [], []
```

**Explanation:**

- Creates unique disposable accounts/class/tests, exercises generation, joining, feedback persistence, retries, student/teacher results and deletion. finally signs out and removes only records created by this run.
- Creates opaque IDs so option identifiers do not reveal correctness/misconception semantics.

## Lines 21–30: account()

```python
    def account(role):
        email, password = f'mathroot-check-{role}-{uuid4().hex}@example.test', uuid4().hex + 'Aa1!'
        created = admin.auth.admin.create_user({'email': email, 'password': password, 'email_confirm': True, 'user_metadata': {'full_name': f'Disposable {role}', 'requested_role': role}}).user
        users.append(str(created.id))
        admin.table('profiles').update({'role': role, 'requested_role': role, 'full_name': f'Disposable {role}'}).eq('id', str(created.id)).execute()
        auth = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_PUBLISHABLE_KEY'])
        session = auth.auth.sign_in_with_password({'email': email, 'password': password}).session
        client = TestClient(app, headers={'Authorization': f'Bearer {session.access_token}'})
        clients.append((client, auth))
        return client
```

**Explanation:**

- Creates a unique disposable live Auth account, prepares its profile, signs in and returns an authenticated test client.
- The bearer header carries the access token. Assessment identity is not a manually entered student ID.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Creates opaque IDs so option identifiers do not reveal correctness/misconception semantics.

## Lines 31–33: ok()

```python
    def ok(response, code=200):
        assert response.status_code == code, f'HTTP {response.status_code}: {response.text[:300]}'
        return response.json()
```

**Explanation:**

- Asserts the expected HTTP status and returns JSON so the smoke test can check its fields.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 34–57: main()

```python
    try:
        teacher, student, outsider = account('teacher'), account('student'), account('student')
        group = ok(teacher.post('/api/classes', params={'class_id': class_id}))
        test = ok(teacher.post('/api/tests', json={'title': 'Disposable live Binomial check', 'class_id': class_id, 'topic_ids': ['binomial'], 'questions_per_topic': 3, 'difficulty': 'easy'}))
        path = f"/api/tests/{test['test_id']}"
        ok(student.get(path), 403)
        ok(student.post('/api/classes/join', json={'class_id': class_id, 'join_code': group['join_code']}))
        assert any(c['class_id'] == class_id for c in ok(student.get('/api/student/classes')))
        assert any(t['test_id'] == test['test_id'] for t in ok(student.get('/api/tests', params={'class_id': class_id})))
        public = ok(student.get(path))
        assert 'correct_option_id' not in str(public)
        for question in public['questions']:
            payload = {'question_id': question['question_id'], 'option_id': question['options'][0]['id']}
            first = ok(student.post(path + '/answers/submit', json=payload))
            again = ok(student.post(path + '/answers/submit', json=payload))
            assert first['selected_option'] == again['selected_option']
            assert first['verification_method'] in ('ai_assisted', 'manual_fallback')
            assert first['feedback'] == again['feedback']
            persisted = admin.table('mathroot_answers').select('verification').eq('test_id', test['test_id']).eq('question_id', question['question_id']).eq('student_id', users[1]).execute().data[0]
            assert persisted['verification']['feedback'] == first['feedback']
        result = ok(student.get(path + '/progress'))
        assert result['status'] == 'Completed' and len(result['answers']) == 3
        assert any(t['test_id'] == test['test_id'] for t in ok(student.get('/api/student/results')))
        report = ok(teacher.get(path + '/results'))
```

**Explanation:**

- Creates unique disposable accounts/class/tests, exercises generation, joining, feedback persistence, retries, student/teacher results and deletion. finally signs out and removes only records created by this run.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- An assertion specifies expected behavior; pytest fails when the observed result differs.

## Lines 58–81: main()

```python
        assert report['student_count'] == report['completed_count'] == report['enrolled_count'] == 1
        assert report['students'][0]['full_name'] == 'Disposable student'
        ok(teacher.get(path + f'/students/{users[1]}'))
        ok(outsider.get(path), 403)
        ok(student.get('/api/teacher/tests'), 403)
        ok(student.delete(path), 403)
        # A second disposable teacher must not inspect or delete this teacher's test.
        other_teacher = account('teacher')
        ok(other_teacher.get(path + '/results'), 403)
        ok(other_teacher.delete(path), 403)
        keep = ok(teacher.post('/api/tests', json={'title': 'Disposable retained check', 'class_id': class_id, 'topic_ids': ['binomial'], 'questions_per_topic': 1, 'difficulty': 'easy'}))
        ok(teacher.delete(path))
        ok(student.get(path), 404)
        assert not admin.table('mathroot_answers').select('test_id').eq('test_id', test['test_id']).execute().data
        assert any(t['test_id'] == keep['test_id'] for t in ok(teacher.get('/api/teacher/tests')))
        print('PASS: live Auth, generation, enrollment, listing, persistence, retry, results, ownership and cascade deletion.')
        print('Generator status:', ok(teacher.get('/api/ai/status')))
    finally:
        for client, auth in clients:
            try: auth.auth.sign_out()
            except Exception: pass
            client.close()
        # Scope cleanup to the unique class and account IDs created by this run.
        admin.table('mathroot_tests').delete().eq('class_id', class_id).execute()
```

**Explanation:**

- Creates unique disposable accounts/class/tests, exercises generation, joining, feedback persistence, retries, student/teacher results and deletion. finally signs out and removes only records created by this run.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 82–86: main()

```python
        admin.table('mathroot_class_members').delete().eq('class_id', class_id).execute()
        admin.table('mathroot_classes').delete().eq('id', class_id).execute()
        for user_id in reversed(users):
            admin.auth.admin.delete_user(user_id)
        print('Disposable live test records cleaned up.')
```

**Explanation:**

- Creates unique disposable accounts/class/tests, exercises generation, joining, feedback persistence, retries, student/teacher results and deletion. finally signs out and removes only records created by this run.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.

## Lines 88–89: Code section

```python
if __name__ == '__main__':
    main()
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Connected files

Follow these imports to their matching code explanations:

- [app/main.py](../app/main.py.md)
- [app/supabase_auth.py](../app/supabase_auth.py.md)

## How to explain this file in the viva

“Optional live workflow check using its own disposable accounts/class/tests. It checks Auth, persistence, results and deletion, then cleans up its own records.”
