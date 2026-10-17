# REST API for Nadula's student and teacher interfaces

Open `http://127.0.0.1:8000/docs` to try these endpoints in Swagger UI.

## GET `/api/topics`
Returns topic IDs, display names, owners and implementation status.

## POST `/api/questions/generate`

```json
{"topic_id":"binomial","difficulty":"easy","class_id":"class-001"}
```

Response (illustrative, values will vary):

```json
{
  "question_id":"uuid-value",
  "topic_id":"binomial",
  "difficulty":"easy",
  "class_id":"class-001",
  "statement":"Expand and simplify: 3(x + 4)",
  "options":[
    {"id":"opaque-id-a","text":"3x + 12"},
    {"id":"opaque-id-b","text":"3x + 4"},
    {"id":"opaque-id-c","text":"x + 12"},
    {"id":"opaque-id-d","text":"3x - 12"}
  ]
}
```

**SECURITY:** Real generated option IDs are opaque UUIDs. The server stores the answer key and misconception mapping privately. The sample IDs above are placeholders, not actual IDs.

## POST `/api/answers/submit`

```json
{"question_id":"uuid-value","option_id":"<opaque-id-from-question>","student_id":"S001"}
```

Returns correctness, suspected misconception, diagnosis status, explanation and recommended next difficulty. A second submit of the same question by the same student returns HTTP 409.

## POST `/api/practice/next`

```json
{"topic_id":"binomial","class_id":"class-001","student_id":"S001"}
```

Generates a fresh follow-up question with difficulty adjusted using the last answered question.

## GET `/api/teacher/summary?class_id=class-001&topic_id=binomial`

Returns attempt counts, number of distinct student IDs, counts of wrong-answer *events* by category, and suggested teacher interventions.

## MVP caveats

- Demo only, no authentication or class ownership yet. Do not put the service on the public internet or input real children's data.
- SQLite is used for local development. Replace with PostgreSQL before production.
- Algebraic question generation and misconception labels are initially deterministic. A trained probabilistic model and optional LLM must be added and evaluated in a later milestone. Do not call the current module a trained AI model.
- The basic adaptive strategy adjusts difficulty; follow-up question selection by information gain is a later milestone.
