"""Common contract that every mathematics-topic module must follow."""
from dataclasses import dataclass
from typing import Literal
from pydantic import BaseModel, Field

Difficulty = Literal['easy', 'medium', 'hard']


@dataclass(frozen=True)
class InternalOption:
    id: str
    text: str
    misconception: str | None = None


@dataclass(frozen=True)
class InternalQuestion:
    id: str
    topic_id: str
    difficulty: str
    statement: str
    options: list[InternalOption]
    correct_option_id: str
    explanation: str
    source_expression: str
    correct_expression: str


class GenerateRequest(BaseModel):
    topic_id: str = 'binomial'
    difficulty: Difficulty = 'easy'
    class_id: str = Field(default='demo-class', min_length=1, max_length=64)


class PublicOption(BaseModel):
    id: str
    text: str


class PublicQuestion(BaseModel):
    question_id: str
    topic_id: str
    difficulty: str
    statement: str
    options: list[PublicOption]
    class_id: str


class AnswerRequest(BaseModel):
    question_id: str
    option_id: str
    student_id: str = Field(min_length=1, max_length=64)


class AnswerResult(BaseModel):
    correct: bool
    selected_option: str
    correct_answer: str
    suspected_misconception: str | None
    diagnosis_status: str
    feedback: str
    recommended_next_difficulty: str


class NextQuestionRequest(BaseModel):
    topic_id: str = 'binomial'
    class_id: str = 'demo-class'
    student_id: str = Field(min_length=1, max_length=64)
