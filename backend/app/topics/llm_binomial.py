"""Compatibility imports; implementation lives in topics/development/binomial/generator.py."""
from app.topics.development.binomial.generator import (
    DEFAULT_MODEL, OLLAMA_URL, SCHEMA, LLMBinomialTopic,
    generator_mode, llm_status, selected_model,
)

__all__ = [
    "DEFAULT_MODEL", "OLLAMA_URL", "SCHEMA", "LLMBinomialTopic",
    "generator_mode", "llm_status", "selected_model",
]
