import random
from dataclasses import asdict
from sympy import Symbol, simplify, sympify
from app.topics.binomial import BinomialTopic
from app.assessments import public_detail

x = Symbol('x')

def test_generated_answers_are_consistent():
    generator = BinomialTopic(random.Random(7))
    for difficulty in ['easy', 'medium', 'hard']:
        for _ in range(100):
            q = generator.generate_question(difficulty)
            assert len(q.options) == 4
            assert len({o.id for o in q.options}) == 4
            assert len({o.text for o in q.options}) == 4
            assert q.correct_option_id in {o.id for o in q.options}
            assert next(o for o in q.options if o.id == q.correct_option_id).misconception is None
            assert simplify(sympify(q.source_expression) - sympify(q.correct_expression)) == 0
            assert len([o for o in q.options if o.misconception is None]) == 1

def test_question_generation_hides_answer():
    question = BinomialTopic().generate_question('easy')
    detail = public_detail({'id': 'test', 'title': 'Test', 'class_id': 'class-A', 'questions': [asdict(question)]}, True)
    assert len(detail['questions'][0]['options']) == 4
    assert 'correct_option_id' not in str(detail)
    assert 'misconception' not in str(detail)
    assert 'explanation' not in str(detail)

def test_topic_ownership(client):
    topics = client.get('/api/topics').json()
    assert len(topics) == 5
    assert sum(item['ready'] for item in topics) == 1
    client.user.update(id='teacher', role='teacher', requested_role='teacher')
    assert client.post('/api/tests', json={'title': 'Invalid topic', 'class_id': 'demo3', 'topic_ids': ['equations'], 'questions_per_topic': 1}).status_code == 422
