"""In-memory PostgREST double; tests never contact or modify live Supabase."""
from copy import deepcopy
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import assessments
from app.supabase_auth import current_user

class Query:
    def __init__(self, db, table):
        self.db, self.name, self.filters = db, table, {}
        self.operation, self.payload, self.window = 'select', None, None
    def select(self, *_): return self
    def eq(self, key, value): self.filters[key] = value; return self
    def limit(self, n): self.window = (0, n - 1); return self
    def range(self, start, end): self.window = (start, end); return self
    def order(self, *_args, **_kwargs): return self
    def insert(self, data): self.operation, self.payload = 'insert', data; return self
    def upsert(self, data, **_kwargs): self.operation, self.payload = 'upsert', data; return self
    def delete(self): self.operation = 'delete'; return self
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
