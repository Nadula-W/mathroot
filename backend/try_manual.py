from app.topics.development.indices_logs.manual import generate_question

for _ in range(5):
    q = generate_question("easy")
    print(q.statement)
    for o in q.options:
        print("   ", o.text, "->", o.misconception)
    print("   explanation:", q.explanation, "\n")