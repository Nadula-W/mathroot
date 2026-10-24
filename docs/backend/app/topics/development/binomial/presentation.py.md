# presentation.py — code explained

**Source:** [backend/app/topics/development/binomial/presentation.py](../../../../../../backend/app/topics/development/binomial/presentation.py) · [All backend explanations](../../../../SOURCE_INDEX.md)

**What and how:** Recognizes known current/historical Binomial source formats with bounded parsing and SymPy consistency checks, reconstructs reviewed English/Sinhala template pairs and matches whole strings. It preserves the existing algebraic fragments and never generates a new question.

Read the actual source blocks in order. Explanations immediately below each block describe its job and connections.



**Bilingual update:** Recognizes known current/historical Binomial source formats with bounded parsing and SymPy consistency checks, reconstructs reviewed English/Sinhala template pairs and matches whole strings. It preserves the existing algebraic fragments and never generates a new question.

## Lines 1–45: Code section

```python
"""Reviewed Sinhala presentation for current and historical Binomial templates.

This module never generates a question or changes an answer. Unknown historical
wording is deliberately left to the shared, fail-closed presentation fallback.
"""
import re

from sympy import Symbol, expand

from app.safe_symbolic import parse_math
from .manual import _as_text


RECOMMENDATIONS = {
    'COEFFICIENT_ERROR': ('Separate the numerical coefficients from the variable, then multiply the coefficients.', 'සංඛ්‍යාත්මක සංගුණක විචල්‍යයෙන් වෙන් කර, සංගුණක ගුණ කරන්න.'),
    'UNLIKE_TERMS': ('Sort terms by variable and power; combine only matching terms.', 'විචල්‍යය සහ බලය අනුව පද වර්ග කර, සමාන පද පමණක් එකතු කරන්න.'),
    'ARITHMETIC_ERROR': ('Recalculate each numerical operation before simplifying the expression.', 'ප්‍රකාශනය සුළු කිරීමට පෙර එක් එක් සංඛ්‍යාත්මක ගණනය නැවත පරීක්ෂා කරන්න.'),
    'VARIABLE_CONSTANT_CONFUSION': ('Label the coefficient, variable and constant in several example expressions.', 'උදාහරණ ප්‍රකාශන කිහිපයක සංගුණකය, විචල්‍යය සහ නියත පදය හඳුනා ගන්න.'),
    'DISTRIBUTION_CONSTANT': ('Demonstrate how the outside coefficient multiplies BOTH bracket terms, then assign two expansion examples.', 'වරහනෙන් පිටත සංගුණකය ඇතුළත පද දෙකටම ගුණ කරන ආකාරය පෙන්වා, ප්‍රසාරණ උදාහරණ දෙකක් ලබා දෙන්න.'),
    'DISTRIBUTION_VARIABLE': ('Review multiplication of coefficients and variables before expanding brackets.', 'වරහන් ප්‍රසාරණයට පෙර සංගුණක සහ විචල්‍ය ගුණ කිරීම නැවත පැහැදිලි කරන්න.'),
    'SIGN_ERROR': ('Revisit signed-number multiplication, then practise bracket expansion with negative constants.', 'ධන හා ඍණ සංඛ්‍යා ගුණ කිරීම නැවත පැහැදිලි කර, ඍණ නියත පද සහිත වරහන් ප්‍රසාරණය පුහුණු කරන්න.'),
}

COMMON = {
    'Keep applying the same procedure carefully.': 'එම ක්‍රමයම සැලකිල්ලෙන් භාවිත කරන්න.',
    'Compare each step with the worked solution.': 'ඔබේ එක් එක් පියවර විසඳුමේ අදාළ පියවර සමඟ සසඳන්න.',
    'Review the worked solution.': 'පියවර සහිත විසඳුම නැවත බලන්න.',
    'Review expansion of brackets with another worked example.': 'තවත් පියවර සහිත උදාහරණයකින් වරහන් ප්‍රසාරණය නැවත බලන්න.',
    'First multiply the variable term, then the constant term, and finally check the signs. Keep unlike terms separate.': 'පළමුව විචල්‍ය පදයත්, ඉන්පසු නියත පදයත් ගුණ කර, අවසානයේ ලකුණු පරීක්ෂා කරන්න. අසමාන පද වෙන්ව තබන්න.',
}
COMMON.update(dict(RECOMMENDATIONS.values()))

PREFIXES = {
    'Correct. You distributed multiplication to both terms. ': 'නිවැරදියි. ඔබ පද දෙකටම ගුණ කර ඇත. ',
    'You may have multiplied the x term but forgotten to multiply the constant. ': 'ඔබ x පදය ගුණ කර, නියත පදය ගුණ කිරීම අමතක කර තිබිය හැක. ',
    'You may have multiplied the constant but forgotten to multiply the x term. ': 'ඔබ නියත පදය ගුණ කර, x පදය ගුණ කිරීම අමතක කර තිබිය හැක. ',
    'You may have changed a sign when multiplying the constant. Review multiplication with negative numbers. ': 'නියත පදය ගුණ කිරීමේදී ලකුණක් වෙනස් වී තිබිය හැක. ඍණ සංඛ්‍යා ගුණ කිරීම නැවත බලන්න. ',
    'Review the distributive law. ': 'වරහනෙන් පිටත සංඛ්‍යාව ඇතුළත පද දෙකටම ගුණ කිරීම නැවත බලන්න. ',
    'Incorrect answer. ': 'පිළිතුර වැරදියි. ',
    'Correct answer. Both terms have been multiplied consistently. ': 'පිළිතුර නිවැරදියි. පද දෙකටම නිවැරදිව ගුණ කර ඇත. ',
    'Possible misconception: multiplying only the variable term. The constant must also be multiplied by the outside coefficient. ': 'ඇති විය හැකි වැරදි අවබෝධය: විචල්‍ය පදය පමණක් ගුණ කිරීම. නියත පදයත් වරහනෙන් පිටත සංගුණකයෙන් ගුණ කළ යුතුය. ',
    'Possible misconception: multiplying only the constant term. Multiply the variable coefficient by the outside coefficient too. ': 'ඇති විය හැකි වැරදි අවබෝධය: නියත පදය පමණක් ගුණ කිරීම. විචල්‍ය පදයේ සංගුණකයත් වරහනෙන් පිටත සංගුණකයෙන් ගුණ කරන්න. ',
    'Possible misconception: a sign error when multiplying signed numbers. Check the signs before simplifying each product. ': 'ඇති විය හැකි වැරදි අවබෝධය: ධන හා ඍණ සංඛ්‍යා ගුණ කිරීමේ ලකුණු දෝෂයක්. එක් එක් ගුණිතය සුළු කිරීමට පෙර ලකුණු පරීක්ෂා කරන්න. ',
    'Incorrect answer. The selection alone does not establish a particular misconception. ': 'පිළිතුර වැරදියි. තෝරාගත් පිළිතුර පමණක් මත නිශ්චිත වැරදි අවබෝධයක් තහවුරු කළ නොහැක. ',
}
```

**Explanation:**

- Recognizes known current/historical Binomial source formats with bounded parsing and SymPy consistency checks, reconstructs reviewed English/Sinhala template pairs and matches whole strings. It preserves the existing algebraic fragments and never generates a new question.

## Lines 46–46: Code section

```python

```

**Explanation:**

- Recognizes known current/historical Binomial source formats with bounded parsing and SymPy consistency checks, reconstructs reviewed English/Sinhala template pairs and matches whole strings. It preserves the existing algebraic fragments and never generates a new question.

## Lines 48–65: _coefficients

```python
def _coefficients(question):
    """Recognize only the two stored source formats; never evaluate arbitrary text."""
    manual = re.fullmatch(r'(-?\d+)\*\(x\+\((-?\d+)\)\)', question.source_expression)
    generated = re.fullmatch(r'\((-?\d+)\)\*\(\((-?\d+)\)\*x\+\((-?\d+)\)\)', question.source_expression)
    if manual:
        a, b = map(int, manual.groups())
        c = 1
    elif generated:
        a, c, b = map(int, generated.groups())
    else:
        raise ValueError('Unrecognized historical Binomial source')
    if any(abs(value) > 10000 for value in (a, c, b)):
        raise ValueError('Unsupported coefficient')
    expected = a * (c * Symbol('x') + b)
    if expand(parse_math(question.source_expression) - expected) != 0 or expand(parse_math(question.correct_expression) - expected) != 0:
        raise ValueError('Inconsistent historical mathematical data')
    return a, c, b

```

**Explanation:**

- Recognizes only known stored Binomial source formats, bounds coefficients and checks source/correct expression consistency with the safe parser and SymPy before rebuilding reviewed text.

## Lines 67–94: _question_texts

```python
def _question_texts(question) -> dict[str, str]:
    a, c, b = _coefficients(question)
    expression = f'{a}({_as_text(c, b)})'
    answer = _as_text(a * c, a * b)
    texts = {
        f'Expand and simplify: {expression}': f'ප්‍රසාරණය කර සුළු කරන්න: {expression}',
    }
    if c == 1:
        texts[
            f'Distribute {a} to BOTH terms: {a} × x = {_as_text(a, 0)} '
            f'and {a} × ({b}) = {a * b}. The answer is {answer}.'
        ] = (
            f'පද දෙකටම {a} ගුණ කරන්න: {a} × x = {_as_text(a, 0)} '
            f'සහ {a} × ({b}) = {a * b}. පිළිතුර {answer} වේ.'
        )
    texts[
        f'Multiply both terms by {a}. {a} × ({_as_text(c, 0)}) '
        f'= {_as_text(a*c, 0)} and {a} × ({b}) = {a*b}. The answer is {answer}.'
    ] = (
        f'පද දෙකම {a} න් ගුණ කරන්න. {a} × ({_as_text(c, 0)}) '
        f'= {_as_text(a*c, 0)} සහ {a} × ({b}) = {a*b}. පිළිතුර {answer} වේ.'
    )
    # Only an exact stored, mathematically checked explanation can be reused.
    explanation = texts.get(question.explanation)
    if explanation:
        texts.update({prefix + question.explanation: translated + explanation for prefix, translated in PREFIXES.items()})
    return texts

```

**Explanation:**

- Constructs exact English/Sinhala pairs for a verified Binomial instruction and worked solution, then known feedback prefixes. Mathematical expression strings are reused unchanged.

## Lines 96–106: presentation_text

```python
def presentation_text(field: str, text: str, question=None, misconception=None) -> str | None:
    """Optional topic hook. Matching full text avoids unsafe substring replacement."""
    if field in {'recommendation', 'action', 'corrective_guidance', 'teaching_recommendation'}:
        if text in COMMON:
            return COMMON[text]
    if question is None:
        return None
    try:
        return _question_texts(question).get(text)
    except (ValueError, SyntaxError, TypeError):
        return None
```

**Explanation:**

- Returns a reviewed whole-string match, including teaching guidance. Unknown or inconsistent wording returns None so the shared layer preserves English and reports a warning.

## How to explain this file in the viva

Recognizes known current/historical Binomial source formats with bounded parsing and SymPy consistency checks, reconstructs reviewed English/Sinhala template pairs and matches whole strings. It preserves the existing algebraic fragments and never generates a new question.
