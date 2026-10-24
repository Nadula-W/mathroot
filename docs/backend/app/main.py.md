# main.py — code explained

**Source:** [backend/app/main.py](../../../backend/app/main.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Uvicorn loads this FastAPI app. It includes the assessment router and adds health/topic/AI-status endpoints plus a readable transport-error response.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–20: Code section

```python
"""MathRoot AI - Supabase backend."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

from app.assessments import router as assessments_router
from app.topics import PLANNED_TOPICS
from app.topics.development.binomial.generator import llm_status


app = FastAPI(
    title="MathRoot AI",
    description="AI-powered O/L Mathematics learning platform",
    version="0.5.0"
)

# Supabase-backed classes, tests, submissions and results.
app.include_router(assessments_router)
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 23–28: upstream_network_error()

```python
@app.exception_handler(httpx.TransportError)
async def upstream_network_error(_request, _exc):
    # Do not retry writes automatically: a lost response can follow a committed write.
    return JSONResponse(status_code=503, content={
        "detail": "Supabase is temporarily unreachable. Please retry. If you submitted an answer, reload the test to check its saved progress."
    })
```

**Explanation:**

- Turns HTTPX transport errors into a readable JSON 503. Writes are not automatically replayed because the database may already have committed.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## Lines 31–36: health()

```python
@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "Supabase PostgreSQL"
    }
```

**Explanation:**

- Returns a server-health message. It does not perform a live database query.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 39–41: topics()

```python
@app.get("/api/topics")
def topics():
    return PLANNED_TOPICS
```

**Explanation:**

- Returns PLANNED_TOPICS for the frontend topic selector.
- The decorator connects this HTTP method/path to the following Python route function.

## Lines 44–46: ai_status()

```python
@app.get("/api/ai/status")
def ai_status():
    return llm_status()
```

**Explanation:**

- Reports local generator model availability through llm_status; it does not generate or grade a question.
- The decorator connects this HTTP method/path to the following Python route function.

## Connected files

Follow these imports to their matching code explanations:

- [app/assessments.py](assessments.py.md)
- [app/topics/__init__.py](topics/__init__.py.md)
- [app/topics/development/binomial/generator.py](topics/development/binomial/generator.py.md)

## How to explain this file in the viva

“Uvicorn loads this FastAPI app. It includes the assessment router and adds health/topic/AI-status endpoints plus a readable transport-error response.”
