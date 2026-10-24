# conftest.py — code explained

**Source:** [backend/tests/conftest.py](../../../backend/tests/conftest.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Query imitates Supabase in memory. The client fixture overrides authentication/database dependencies so unit tests do not modify live student records.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–8: Code section

```python
"""In-memory PostgREST double; tests never contact or modify live Supabase."""
from copy import deepcopy
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import assessments
from app.supabase_auth import current_user
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 10–10: Query

```python
class Query:
```

**Explanation:**

- An in-memory Supabase query double. Its chainable methods build a request; execute applies filters/operations to Python lists and imitates unique-key/cascade behavior.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 11–13: __init__()

```python
    def __init__(self, db, table):
        self.db, self.name, self.filters = db, table, {}
        self.operation, self.payload, self.window = 'select', None, None
```

**Explanation:**

- Initializes the instance fields shown here. The manual topic accepts an injected random source for repeatable tests, otherwise using SystemRandom; fake helpers initialize their own recorded state.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 14–14: select()

```python
    def select(self, *_): return self
```

**Explanation:**

- Accepts the select call and returns self for chaining.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 15–15: eq()

```python
    def eq(self, key, value): self.filters[key] = value; return self
```

**Explanation:**

- Stores an equality filter for execute.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 16–16: limit()

```python
    def limit(self, n): self.window = (0, n - 1); return self
```

**Explanation:**

- Sets a maximum result window.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 17–17: range()

```python
    def range(self, start, end): self.window = (start, end); return self
```

**Explanation:**

- Sets the inclusive row window.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 18–18: order()

```python
    def order(self, *_args, **_kwargs): return self
```

**Explanation:**

- Accepts ordering syntax for API compatibility; this simple test fake does not sort.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 19–19: insert()

```python
    def insert(self, data): self.operation, self.payload = 'insert', data; return self
```

**Explanation:**

- Records the insert operation and payload.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 20–20: upsert()

```python
    def upsert(self, data, **_kwargs): self.operation, self.payload = 'upsert', data; return self
```

**Explanation:**

- Records an insert-or-existing membership operation.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 21–21: delete()

```python
    def delete(self): self.operation = 'delete'; return self
```

**Explanation:**

- Marks a delete to apply in execute.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 22–38: execute()

```python
    def execute(self):
        rows = self.db.setdefault(self.name, [])
        matched = [r for r in rows if all(r.get(k) == v for k, v in self.filters.items())]
        if self.operation in ('insert', 'upsert'):
            row = {**self.payload, 'created_at': '2026-10-21T10:00:00Z'}
            keys = ('test_id', 'question_id', 'student_id') if self.name == 'mathroot_answers' else ('class_id', 'student_id')
            duplicate = next((r for r in rows if all(r.get(k) == row.get(k) for k in keys)), None)
            if duplicate and self.operation == 'insert' and self.name == 'mathroot_answers': raise ValueError('duplicate key')
            if not duplicate or self.operation == 'insert': rows.append(row)
            matched = [row]
        if self.operation == 'delete':
            self.db[self.name] = [r for r in rows if r not in matched]
            if self.name == 'mathroot_tests':
                ids = {r['id'] for r in matched}
                self.db['mathroot_answers'] = [r for r in self.db.get('mathroot_answers', []) if r['test_id'] not in ids]
        if self.window: matched = matched[self.window[0]:self.window[1] + 1]
        return SimpleNamespace(data=deepcopy(matched))
```

**Explanation:**

- Applies filters/operations to in-memory records, imitates duplicate keys and answer cascade deletion, slices the requested page and returns .data.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 40–52: client()

```python
@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'manual')
    db = {'mathroot_classes': [{'id': 'demo3', 'teacher_id': 'teacher', 'join_code': 'secret-code'}],
          'profiles': [{'id': 'teacher', 'full_name': 'Teacher'}, {'id': 'student', 'full_name': 'Student Name'}]}
    monkeypatch.setattr(assessments, 'admin_client', lambda: SimpleNamespace(table=lambda name: Query(db, name)))
    user = {'id': 'student', 'role': 'student', 'requested_role': 'student'}
    app.dependency_overrides[current_user] = lambda: user.copy()
    with TestClient(app) as test_client:
        test_client.db = db
        test_client.user = user
        yield test_client
    app.dependency_overrides.clear()
```

**Explanation:**

- Builds in-memory records, replaces the database client and current_user dependency, and defaults feedback to manual mode. yield gives the client to tests; cleanup clears overrides.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.
- Supplies the prepared client to the test; code after yield cleans up overrides.
- Replaces real authentication only inside tests. Clearing overrides restores normal application dependencies.

## Connected files

Follow these imports to their matching code explanations:

- [app/main.py](../app/main.py.md)
- [app/supabase_auth.py](../app/supabase_auth.py.md)

## How to explain this file in the viva

“Query imitates Supabase in memory. The client fixture overrides authentication/database dependencies so unit tests do not modify live student records.”
