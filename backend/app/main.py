
"""MathRoot AI - Supabase backend."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

from app.assessments import router as assessments_router
from app.topics import PLANNED_TOPICS
from app.topics.llm_binomial import llm_status


app = FastAPI(
    title="MathRoot AI",
    description="AI-powered O/L Mathematics learning platform",
    version="0.5.0"
)

# Supabase-backed classes, tests, submissions and results.
app.include_router(assessments_router)


@app.exception_handler(httpx.TransportError)
async def upstream_network_error(_request, _exc):
    # Do not retry writes automatically: a lost response can follow a committed write.
    return JSONResponse(status_code=503, content={
        "detail": "Supabase is temporarily unreachable. Please retry. If you submitted an answer, reload the test to check its saved progress."
    })


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "Supabase PostgreSQL"
    }


@app.get("/api/topics")
def topics():
    return PLANNED_TOPICS


@app.get("/api/ai/status")
def ai_status():
    return llm_status()
