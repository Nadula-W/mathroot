# safe_symbolic.py — code explained

**Source:** [backend/app/safe_symbolic.py](../../../backend/app/safe_symbolic.py) · [All backend explanations](../SOURCE_INDEX.md)

**What and how:** Restricted AST-to-SymPy parsing for future free-text adapters. It does not execute input as Python. Current MCQ submission does not use this module.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–9: Code section

```python
"""Bounded polynomial/rational expression parsing for future free-text adapters.

No eval, sympify(string), parse_expr, functions, attributes or arbitrary symbols.
Not wired to the current MCQ-only submission contract.
"""
import ast
import re

from sympy import Integer, Symbol, cancel
```

**Explanation:**

- Imports connect this file to the named helpers/components. app.* imports start from the backend package; . imports use the current package.

## Lines 12–18: parse_math()

```python
def parse_math(text: str, variables: tuple[str, ...] = ("x",)):
    if len(text) > 200 or not re.fullmatch(r"[A-Za-z0-9_+*/().\s-]+", text):
        raise ValueError("Unsupported expression")
    tree = ast.parse(text, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Expression too complex")
    symbols = {name: Symbol(name) for name in variables}
```

**Explanation:**

- Bounds size/characters/tree complexity, then converts only whitelisted syntax to SymPy objects. No eval or untrusted sympify(string) is used.
- Builds a syntax tree for inspection, not execution. convert accepts only the explicitly whitelisted nodes.

## Lines 20–38: convert()

```python
    def convert(node):
        if isinstance(node, ast.Constant) and type(node.value) is int and abs(node.value) <= 10000:
            return Integer(node.value)
        if isinstance(node, ast.Name) and node.id in symbols:
            return symbols[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = convert(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                if not isinstance(node.right, ast.Constant) or type(node.right.value) is not int or not 0 <= node.right.value <= 6:
                    raise ValueError("Unsupported exponent")
            left, right = convert(node.left), convert(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div) and right != 0: return left / right
            if isinstance(node.op, ast.Pow): return left ** right
        raise ValueError("Unsupported expression syntax")
```

**Explanation:**

- Recursively accepts bounded integers, declared variables and supported arithmetic. Functions, attributes, unsafe exponents and zero denominators are rejected.
- Only bounded integer/symbol/arithmetic node types are converted. Arbitrary calls or attributes are rejected.
- Line 21: Checks exact integer type so booleans are not treated as integers, and limits magnitude before conversion.
- Line 30: Allows only small constant nonnegative exponents; expressions such as x**x or extremely large powers are rejected.

## Lines 40–43: parse_math()

```python
    # Bound polynomial growth before invoking any algebraic simplification.
    if sum(isinstance(n, ast.Pow) for n in ast.walk(tree)) > 2:
        raise ValueError("Too many powers")
    return convert(tree.body)
```

**Explanation:**

- Bounds size/characters/tree complexity, then converts only whitelisted syntax to SymPy objects. No eval or untrusted sympify(string) is used.
- Line 41: In the symbolic-parser power-count check, more than two power nodes are rejected to limit algebraic growth.
- Line 43: Begins recursive conversion at the expression root only after the size/syntax-complexity checks passed.

## Lines 46–48: equivalent()

```python
def equivalent(student: str, expected: str, variables: tuple[str, ...] = ("x",)) -> bool:
    """Algebraic equivalence on the common domain; domain restrictions need topic rules."""
    return cancel(parse_math(student, variables) - parse_math(expected, variables)) == 0
```

**Explanation:**

- Safely parses both expressions and uses cancel on their difference. Equality on the common domain does not replace topic-specific domain restrictions.
- Simplifies the expression difference to test algebraic equality on the common domain.

## How to explain this file in the viva

“Restricted AST-to-SymPy parsing for future free-text adapters. It does not execute input as Python. Current MCQ submission does not use this module.”
