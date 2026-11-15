"""Each teammate adds a topic module here without changing API routes."""
from app.topics.development.binomial.generator import LLMBinomialTopic
TOPICS = {
      "binomial": LLMBinomialTopic(),
}

PLANNED_TOPICS = [
    {'id': 'binomial', 'name': 'Binomial Expressions', 'owner': 'Nadula', 'ready': True},
    {'id': 'factorization', 'name': 'Factors of Quadratic Expressions', 'owner': 'Bopage', 'ready': False},
    {'id': 'equations', 'name': 'Equations', 'owner': 'Nimsara', 'ready': False},
    {'id': 'algebraic_fractions', 'name': 'Algebraic Fractions', 'owner': 'Fernando', 'ready': False},
    {'id': 'indices_logs', 'name': 'Indices and Logarithms', 'owner': 'Sadeepa', 'ready': False},
]
