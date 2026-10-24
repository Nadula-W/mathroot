# requirements.txt — code explained

**Source:** [backend/requirements.txt](../../backend/requirements.txt) · [All backend explanations](SOURCE_INDEX.md)

**What and how:** Lists FastAPI, Uvicorn, SymPy, pytest and HTTPX dependencies. The current code also imports supabase/python-dotenv, installed locally but not yet listed here.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–5: Code section

```text
fastapi>=0.115,<1
uvicorn[standard]>=0.34,<1
sympy>=1.13,<2
pytest>=8,<10
httpx>=0.27,<1
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## How to explain this file in the viva

“Lists FastAPI, Uvicorn, SymPy, pytest and HTTPX dependencies. The current code also imports supabase/python-dotenv, installed locally but not yet listed here.”
