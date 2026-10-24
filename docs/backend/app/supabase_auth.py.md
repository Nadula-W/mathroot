# supabase_auth.py — code explained

**Source:** [backend/app/supabase_auth.py](../../../backend/app/supabase_auth.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Verifies bearer tokens and approved profile roles. Cached public/privileged clients share pooled HTTP/1.1 connections. Only backend code uses the secret key.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–16: Code section

```python
"""Supabase Auth verification and server-only database access for MathRoot."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from supabase import Client, ClientOptions, create_client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

bearer = HTTPBearer(auto_error=False)
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.
- The bearer header carries the access token. Assessment identity is not a manually entered student ID.

## Lines 19–26: client_options()

```python
def client_options() -> ClientOptions:
    # Avoid the shared HTTP/2 stream failure seen with concurrent Windows requests.
    # HTTPX clients are thread-safe; keep connection pooling over HTTP/1.1.
    return ClientOptions(httpx_client=httpx.Client(
        http2=False,
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    ))
```

**Explanation:**

- Uses pooled HTTP/1.1 with bounded connection/read waits to avoid the observed concurrent Windows HTTP/2 socket failure.
- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 29–31: public_client()

```python
@lru_cache
def public_client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_PUBLISHABLE_KEY"], options=client_options())
```

**Explanation:**

- Creates/caches the public Supabase client used to verify access tokens.
- Reuses the created Supabase client and connection pool instead of recreating them for each request.

## Lines 34–37: admin_client()

```python
@lru_cache
def admin_client() -> Client:
    # Do not use this client in the browser or reveal this secret in git.
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"], options=client_options())
```

**Explanation:**

- Creates/caches the privileged backend database client. It bypasses RLS, so all callers must perform server permission checks.
- Reuses the created Supabase client and connection pool instead of recreating them for each request.

## Lines 40–63: current_user()

```python
def current_user(
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Please log in.")
    try:
        response = public_client().auth.get_user(authorization.credentials)
        user = response.user
        if not user:
            raise HTTPException(401, "Invalid login session.")
    except HTTPException:
        raise
    except httpx.TransportError as exc:
        raise HTTPException(503, "Authentication service is temporarily unavailable. Please retry.") from exc
    except Exception as exc:
        raise HTTPException(401, "Login session could not be verified. Please log in again.") from exc
    try:
        rows = (
            admin_client().table("profiles")
            .select("id,role,requested_role,full_name")
            .eq("id", str(user.id)).limit(1).execute().data
        ) or []
        if not rows:
            raise HTTPException(403, "User profile not found.")
```

**Explanation:**

- Requires a bearer token, verifies it with Supabase Auth and loads its matching profile. Login errors use 401, profile/access errors use 403, and service failures use 503.
- The bearer header carries the access token. Assessment identity is not a manually entered student ID.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Begins an operation on the named Supabase table. select/insert/delete and the filters specify the operation.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Sends the built query. .data contains returned rows, with or [] normalizing empty results.
- Stops the success path with the specified HTTP error status and readable detail.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 64–68: current_user()

```python
        return {**rows[0], "id": str(user.id)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, "Your profile could not be loaded. Please try again.") from exc
```

**Explanation:**

- Requires a bearer token, verifies it with Supabase Auth and loads its matching profile. Login errors use 401, profile/access errors use 403, and service failures use 503.
- Stops the success path with the specified HTTP error status and readable detail.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 71–74: require_teacher()

```python
def require_teacher(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "teacher":
        raise HTTPException(403, "Approved teacher account required.")
    return user
```

**Explanation:**

- Accepts only approved role=teacher; requested_role alone is insufficient.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Stops the success path with the specified HTTP error status and readable detail.

## Lines 77–80: require_student()

```python
def require_student(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "student" or user["requested_role"] == "teacher":
        raise HTTPException(403, "Student account required.")
    return user
```

**Explanation:**

- Accepts student accounts and excludes pending teacher applicants.
- FastAPI resolves the declared authentication dependencies before running the route body.
- Stops the success path with the specified HTTP error status and readable detail.

## How to explain this file in the viva

“Verifies bearer tokens and approved profile roles. Cached public/privileged clients share pooled HTTP/1.1 connections. Only backend code uses the secret key.”
