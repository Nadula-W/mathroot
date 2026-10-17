"""Small local SQLite store for a runnable prototype.

Move to PostgreSQL and add proper authentication BEFORE real student deployment.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from app.contracts import InternalQuestion, InternalOption

DEFAULT_PATH = Path(__file__).resolve().parent.parent / 'mathroot_dev.sqlite3'


def db_path() -> Path:
    return Path(os.getenv('MATHROOT_DB_PATH', str(DEFAULT_PATH)))


@contextmanager
def db():
    p = db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(p))
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize():
    with db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY, class_id TEXT NOT NULL, topic_id TEXT NOT NULL,
            difficulty TEXT NOT NULL, data TEXT NOT NULL)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question_id TEXT NOT NULL,
            class_id TEXT NOT NULL, student_id TEXT NOT NULL,
            option_id TEXT NOT NULL, correct INTEGER NOT NULL,
            misconception TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(question_id, student_id))''')


def save_question(question: InternalQuestion, class_id: str):
    data = {
        'id': question.id, 'topic_id': question.topic_id,
        'difficulty': question.difficulty, 'statement': question.statement,
        'options': [vars(option) for option in question.options],
        'correct_option_id': question.correct_option_id,
        'explanation': question.explanation,
        'source_expression': question.source_expression,
        'correct_expression': question.correct_expression,
    }
    with db() as conn:
        conn.execute('INSERT INTO questions VALUES (?, ?, ?, ?, ?)',
                     (question.id, class_id, question.topic_id, question.difficulty, json.dumps(data)))


def get_question(question_id: str):
    with db() as conn:
        row = conn.execute('SELECT class_id, data FROM questions WHERE id = ?', (question_id,)).fetchone()
    if row is None:
        return None
    data = json.loads(row['data'])
    data['options'] = [InternalOption(**option) for option in data['options']]
    return InternalQuestion(**data), row['class_id']


def save_answer(question_id, class_id, student_id, option_id, correct, misconception):
    with db() as conn:
        conn.execute('''INSERT INTO answers
          (question_id, class_id, student_id, option_id, correct, misconception)
          VALUES (?, ?, ?, ?, ?, ?)''',
          (question_id, class_id, student_id, option_id, int(correct), misconception))


def previous_misconceptions(class_id: str, student_id: str, topic_id: str) -> list[str]:
    with db() as conn:
        rows = conn.execute('''SELECT a.misconception FROM answers a
          JOIN questions q ON a.question_id = q.id
          WHERE a.class_id = ? AND a.student_id = ? AND q.topic_id = ?
            AND a.misconception IS NOT NULL''', (class_id, student_id, topic_id)).fetchall()
    return [row['misconception'] for row in rows]


def last_answer_correct(class_id: str, student_id: str, topic_id: str):
    with db() as conn:
        row = conn.execute('''SELECT a.correct, q.difficulty FROM answers a
          JOIN questions q ON a.question_id = q.id
          WHERE a.class_id = ? AND a.student_id = ? AND q.topic_id = ?
          ORDER BY a.id DESC LIMIT 1''', (class_id, student_id, topic_id)).fetchone()
    return None if row is None else (bool(row['correct']), row['difficulty'])


def summary_for_class(class_id: str, topic_id: str):
    with db() as conn:
        counts = conn.execute('''SELECT a.misconception, COUNT(*) AS n FROM answers a
           JOIN questions q ON q.id = a.question_id
           WHERE a.class_id = ? AND q.topic_id = ? AND a.misconception IS NOT NULL
           GROUP BY a.misconception ORDER BY n DESC''', (class_id, topic_id)).fetchall()
        overall = conn.execute('''SELECT COUNT(*) AS answers, COUNT(DISTINCT a.student_id) AS students,
          SUM(a.correct) AS correct_answers FROM answers a
          JOIN questions q ON q.id = a.question_id
          WHERE a.class_id = ? AND q.topic_id = ?''', (class_id, topic_id)).fetchone()
    return {
        'total_answers': overall['answers'],
        'students': overall['students'],
        'correct_answers': overall['correct_answers'] or 0,
        'misconception_counts': [{'code': r['misconception'], 'answer_count': r['n']} for r in counts],
    }
