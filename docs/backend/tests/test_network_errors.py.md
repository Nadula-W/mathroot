# test_network_errors.py — code explained

**Source:** [backend/tests/test_network_errors.py](../../../backend/tests/test_network_errors.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Simulates network failures and checks pooled HTTP/1.1 plus readable 503 responses without leaking socket details.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–8: Code section

```python
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app import assessments, supabase_auth
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.
- The bearer header carries the access token. Assessment identity is not a manually entered student ID.

## Lines 11–13: test_supabase_clients_use_http1()

```python
def test_supabase_clients_use_http1(monkeypatch):
    captured = []
    real_client = httpx.Client
```

**Explanation:**

- Tests that supabase clients use http1. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 15–17: capture()

```python
    def capture(**kwargs):
        captured.append(kwargs)
        return real_client(**kwargs)
```

**Explanation:**

- Defines capture with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 19–25: test_supabase_clients_use_http1()

```python
    monkeypatch.setattr(supabase_auth.httpx, "Client", capture)
    options = supabase_auth.client_options()
    try:
        assert captured[0]["http2"] is False
        assert options.httpx_client.timeout.connect == 10
    finally:
        options.httpx_client.close()
```

**Explanation:**

- Tests that supabase clients use http1. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 28–28: test_database_socket_failure_returns_readable_503()

```python
def test_database_socket_failure_returns_readable_503(client, monkeypatch):
```

**Explanation:**

- Tests that database socket failure returns readable 503. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 29–30: fail()

```python
    def fail(*args, **kwargs):
        raise httpx.ReadError("Windows socket failure")
```

**Explanation:**

- Defines fail with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 32–36: test_database_socket_failure_returns_readable_503()

```python
    monkeypatch.setattr(assessments, "answer_rows", fail)
    response = client.get("/api/student/results")
    assert response.status_code == 503
    assert "temporarily unreachable" in response.json()["detail"]
    assert "Windows socket" not in response.text
```

**Explanation:**

- Tests that database socket failure returns readable 503. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 39–39: test_auth_network_failure_does_not_report_invalid_login()

```python
def test_auth_network_failure_does_not_report_invalid_login(monkeypatch):
```

**Explanation:**

- Tests that auth network failure does not report invalid login. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## Lines 40–41: fail()

```python
    def fail(*args):
        raise httpx.ConnectError("Offline")
```

**Explanation:**

- Defines fail with the inputs shown in its signature. The code sections below explain the calls, conditions and returned values in source order.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 43–46: test_auth_network_failure_does_not_report_invalid_login()

```python
    monkeypatch.setattr(supabase_auth, "public_client", lambda: SimpleNamespace(auth=SimpleNamespace(get_user=fail)))
    with pytest.raises(HTTPException) as error:
        supabase_auth.current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token"))
    assert error.value.status_code == 503
```

**Explanation:**

- Tests that auth network failure does not report invalid login. Read the setup, the operation under test and then the assertions: they state what the working implementation must preserve.
- The bearer header carries the access token. Assessment identity is not a manually entered student ID.
- An assertion specifies expected behavior; pytest fails when the observed result differs.
- Temporarily replaces dependencies/settings for deterministic tests and restores them afterward.

## How to explain this file in the viva

“Simulates network failures and checks pooled HTTP/1.1 plus readable 503 responses without leaking socket details.”
