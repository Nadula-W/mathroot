"""Example clean entry point for Supabase-backed assessments only.

Use the same TOPICS registration you already have, including your Ollama
LLMBinomialTopic. The old SQLite practice demo is deliberately excluded.
"""
from fastapi import FastAPI
from app.assessments import router as assessments_router
from app.topics import PLANNED_TOPICS
from app.topics.llm_binomial import llm_status

app = FastAPI(title="MathRoot AI", version="0.5.0")
app.include_router(assessments_router)

@app.get("/health")
def health():
    return {"status": "ok", "database": "Supabase PostgreSQL"}

@app.get("/api/topics")
def topics():
    return PLANNED_TOPICS

@app.get("/api/ai/status")
def ai_status():
    return llm_status()
