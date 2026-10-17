"""MathRoot first runnable API. Local demo only: NO authentication yet."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from sqlite3 import IntegrityError

from app import storage
from app.contracts import (
    GenerateRequest, AnswerRequest, PublicQuestion, PublicOption,
    AnswerResult, NextQuestionRequest,
)
from app.topics import TOPICS, PLANNED_TOPICS


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.initialize()
    yield


app = FastAPI(title='MathRoot AI API', version='0.1.0', lifespan=lifespan)


@app.get('/health')
def health():
    return {'status': 'ok', 'version': '0.1.0'}


@app.get('/api/topics')
def topics():
    return PLANNED_TOPICS


def create_public_question(topic_id: str, difficulty: str, class_id: str) -> PublicQuestion:
    topic = TOPICS.get(topic_id)
    if topic is None:
        raise HTTPException(status_code=422, detail='Topic is not implemented yet.')
    question = topic.generate_question(difficulty)
    storage.save_question(question, class_id)
    return PublicQuestion(
        question_id=question.id, topic_id=question.topic_id,
        difficulty=question.difficulty, class_id=class_id,
        statement=question.statement,
        options=[PublicOption(id=o.id, text=o.text) for o in question.options],
    )


@app.post('/api/questions/generate', response_model=PublicQuestion)
def generate_question(req: GenerateRequest):
    return create_public_question(req.topic_id, req.difficulty, req.class_id)


@app.post('/api/answers/submit', response_model=AnswerResult)
def submit_answer(req: AnswerRequest):
    stored = storage.get_question(req.question_id)
    if stored is None:
        raise HTTPException(status_code=404, detail='Question not found.')
    question, class_id = stored
    option = next((o for o in question.options if o.id == req.option_id), None)
    if option is None:
        raise HTTPException(status_code=422, detail='Unknown answer option.')
    topic = TOPICS.get(question.topic_id)
    if topic is None:
        raise HTTPException(status_code=422, detail='Topic module unavailable.')
    is_correct = req.option_id == question.correct_option_id
    misconception = None if is_correct else option.misconception
    try:
        storage.save_answer(question.id, class_id, req.student_id, req.option_id, is_correct, misconception)
    except IntegrityError:
        raise HTTPException(status_code=409, detail='This student already answered this question.')

    evidence_count = (storage.previous_misconceptions(class_id, req.student_id, question.topic_id)
                      .count(misconception) if misconception else 0)
    status = 'none' if is_correct else ('repeated_signal' if evidence_count >= 2 else 'suspected')
    difficulties = ['easy', 'medium', 'hard']
    current_index = difficulties.index(question.difficulty)
    next_difficulty = difficulties[min(2, current_index + 1)] if is_correct else difficulties[max(0, current_index - 1)]
    answer_text = next(o.text for o in question.options if o.id == question.correct_option_id)
    return AnswerResult(
        correct=is_correct, selected_option=option.text, correct_answer=answer_text,
        suspected_misconception=misconception, diagnosis_status=status,
        feedback=topic.feedback(question, misconception),
        recommended_next_difficulty=next_difficulty,
    )


@app.post('/api/practice/next', response_model=PublicQuestion)
def next_question(req: NextQuestionRequest):
    previous = storage.last_answer_correct(req.class_id, req.student_id, req.topic_id)
    if previous is None:
        difficulty = 'easy'
    else:
        correct, old_difficulty = previous
        values = ['easy', 'medium', 'hard']
        idx = values.index(old_difficulty)
        difficulty = values[min(2, idx + 1)] if correct else values[max(0, idx - 1)]
    return create_public_question(req.topic_id, difficulty, req.class_id)


@app.get('/api/teacher/summary')
def teacher_summary(class_id: str = Query(min_length=1, max_length=64), topic_id: str = 'binomial'):
    topic = TOPICS.get(topic_id)
    if topic is None:
        raise HTTPException(status_code=422, detail='Topic is not implemented yet.')
    summary = storage.summary_for_class(class_id, topic_id)
    summary['class_id'] = class_id
    summary['topic_id'] = topic_id
    summary['recommendations'] = [
        {'code': item['code'], 'action': topic.teaching_recommendation(item['code'])}
        for item in summary['misconception_counts']
    ]
    summary['note'] = 'Counts are wrong-answer events, not confirmed diagnoses or unique students.'
    return summary
