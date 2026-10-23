"""Bounded polynomial/rational expression parsing for future free-text adapters.

No eval, sympify(string), parse_expr, functions, attributes or arbitrary symbols.
Not wired to the current MCQ-only submission contract.
"""
import ast
import re

from sympy import Integer, Symbol, cancel


def parse_math(text: str, variables: tuple[str, ...] = ("x",)):
    if len(text) > 200 or not re.fullmatch(r"[A-Za-z0-9_+*/().\s-]+", text):
        raise ValueError("Unsupported expression")
    tree = ast.parse(text, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Expression too complex")
    symbols = {name: Symbol(name) for name in variables}

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

    # Bound polynomial growth before invoking any algebraic simplification.
    if sum(isinstance(n, ast.Pow) for n in ast.walk(tree)) > 2:
        raise ValueError("Too many powers")
    return convert(tree.body)


def equivalent(student: str, expected: str, variables: tuple[str, ...] = ("x",)) -> bool:
    """Algebraic equivalence on the common domain; domain restrictions need topic rules."""
    return cancel(parse_math(student, variables) - parse_math(expected, variables)) == 0
