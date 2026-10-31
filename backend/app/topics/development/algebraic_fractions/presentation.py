"""Reviewed Sinhala presentation for current and historical Algebraic Fractions templates.

This module never generates a question or changes an answer. Unknown historical
or dynamic wording is deliberately left to the shared, fail-closed presentation fallback.
"""
import re

from . import manual

RECOMMENDATIONS = {
    "DENOMINATOR_ADDITION": (
        "Review numerical fraction addition with visual area models to reinforce why denominators do not add, "
        "then transition to algebraic fractions with like denominators (e.g., 1/x + 2/x).",
        "හරයන් එකතු නොවන හේතුව පැහැදිලි කිරීමට දෘශ්‍ය ආකෘති භාවිතයෙන් සංඛ්‍යාත්මක භාග එකතු කිරීම නැවත මතක් කර, "
        "පසුව සමාන හර සහිත වීජීය භාග වෙත යොමු වන්න (උදා. 1/x + 2/x)."
    ),
    "UNSCALED_NUMERATOR": (
        "Have students practice finding equivalent fractions by multiplying both numerator and denominator "
        "by the necessary scaling factor before combining.",
        "භාග එකතු කිරීමට පෙර අවශ්‍ය සාධකයෙන් ලවය සහ හරය යන දෙකම ගුණ කර තුල්‍ය භාග සෙවීම සිසුන්ට පුහුණු කරන්න."
    ),
    "SIGN_ERROR": (
        "Have students write the operation between fractions explicitly and check signed-number addition and "
        "subtraction before combining numerators.",
        "භාග අතර ඇති ලකුණ පැහැදිලිව ලියා, ලවයන් සුළු කිරීමට පෙර ධන හා ඍණ සංඛ්‍යා එකතු කිරීම සහ අඩු කිරීම නැවත පරීක්ෂා කිරීමට සිසුන්ට උපදෙස් දෙන්න."
    ),
    "SIGN_DISTRIBUTION_ERROR": (
        "Demonstrate placing parentheses around the entire subtracted numerator, showing step-by-step how the "
        "subtraction sign distributes to every term.",
        "අඩු කරනු ලබන මුළු ලවය වටා වරහන් යොදන ආකාරයත්, ඍණ ලකුණ එක් එක් පදයට බෙදී යන ආකාරයත් පියවරෙන් පියවර පෙන්වා දෙන්න."
    ),
    "NUMERATOR_OPERATION_CONFUSION": (
        "Contrast fraction addition and fraction multiplication side by side to reinforce when numerators are added "
        "versus when they are multiplied.",
        "ලවයන් එකතු කරන්නේ කවදාද සහ ගුණ කරන්නේ කවදාද යන්න පැහැදිලි කිරීමට භාග එකතු කිරීම සහ භාග ගුණ කිරීම එකිනෙක සංසන්දනය කර පෙන්වන්න."
    ),
}

FALLBACK_RECOMMENDATION = (
    "Review algebraic fraction simplification with another worked example and guided practice.",
    "තවත් පියවර සහිත උදාහරණයක් සහ මඟපෙන්වන ලද පුහුණුවක් සමඟ වීජීය භාග සුළු කිරීම නැවත ආවර්ජනය කරන්න."
)

COMMON = {
    "Keep applying the same procedure carefully.": "එම ක්‍රමයම සැලකිල්ලෙන් භාවිත කරන්න.",
    "Compare each step with the worked solution.": "ඔබේ එක් එක් පියවර විසඳුමේ අදාළ පියවර සමඟ සසඳන්න.",
    "Review the worked solution.": "පියවර සහිත විසඳුම නැවත බලන්න.",
}
COMMON.update(dict(RECOMMENDATIONS.values()))
COMMON[FALLBACK_RECOMMENDATION[0]] = FALLBACK_RECOMMENDATION[1]

PREFIXES = {
    "Correct. You simplified the algebraic fraction properly. ": "නිවැරදියි. ඔබ වීජීය භාගය නිවැරදිව සුළු කර ඇත. ",
    "You may have added the denominators directly across fractions. Remember that fractions can only be combined over a common denominator; denominators do not add together. ": "ඔබ භාගවල හරයන් එකිනෙක කෙලින්ම එකතු කර තිබිය හැක. භාග එකතු කළ හැක්කේ පොදු හරයක් සහිතව පමණක් බව මතක තබා ගන්න; හරයන් කෙලින්ම එකතු නොවේ. ",
    "You may have converted to a common denominator without scaling the numerator. When you multiply the denominator by a factor, you must multiply the numerator by the same factor to maintain equivalence. ": "ඔබ ලවය අදාළ සාධකයෙන් ගුණ නොකර පොදු හරයකට ගෙන තිබිය හැක. හරය යම් සාධකයකින් ගුණ කරන විට තුල්‍යතාවය රැක ගැනීමට ලවයද එම සාධකයෙන්ම ගුණ කළ යුතුය. ",
    "You may have made a sign error when combining the numerators. Carefully check whether you should be adding or subtracting the terms. ": "ලවයන් සුළු කිරීමේදී ලකුණු දෝෂයක් සිදුවී තිබිය හැක. පද එකතු කළ යුතුද අඩු කළ යුතුද යන්න පිළිබඳව සැලකිලිමත් වන්න. ",
    "You may have forgotten to distribute the negative sign to all terms in the second numerator. When subtracting a binomial numerator, the negative sign must be distributed across both terms. ": "දෙවන ලවයේ සියලුම පද සඳහා ඍණ ලකුණ බෙදා හැරීම ඔබට අමතක වී තිබිය හැක. ද්විපද ලවයක් අඩු කිරීමේදී ඍණ ලකුණ පද දෙකටම බෙදී යා යුතුය. ",
    "You may have multiplied the numerators instead of adding or subtracting them. When adding or subtracting fractions over a common denominator, combine the numerators using addition or subtraction, not multiplication. ": "ලවයන් එකතු කිරීම හෝ අඩු කිරීම වෙනුවට ඔබ ඒවා ගුණ කර තිබිය හැක. පොදු හරයක් සහිත භාග එකතු කිරීමේදී හෝ අඩු කිරීමේදී ලවයන් එකතු කිරීම හෝ අඩු කිරීම පමණක් කළ යුතුය. ",
    "Review the rules for combining and simplifying algebraic fractions. ": "වීජීය භාග එකතු කිරීම සහ සුළු කිරීමේ නීති නැවත බලන්න. ",
    "Incorrect answer. ": "පිළිතුර වැරදියි. ",
}


def _parse_question(question):
    src = getattr(question, "source_expression", None)
    if src:
        src = src.strip()
        m = re.fullmatch(r"(\d+)/x\s*\+\s*(\d+)/x", src)
        if m:
            return "easy", (int(m.group(1)), int(m.group(2)))
        m = re.fullmatch(r"(\d+)/x\s*-\s*(\d+)/\(\s*(\d+)\s*\*\s*x\s*\)", src)
        if m:
            return "medium", (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m = re.fullmatch(r"(\d+)/\(\s*x\s*\+\s*(\d+)\s*\)\s*-\s*(\d+)/\(\s*x\s*\+\s*(\d+)\s*\)", src)
        if m:
            return "hard", (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))

    stmt = getattr(question, "statement", None)
    if stmt:
        stmt = stmt.strip()
        m = re.fullmatch(r"Simplify:\s*(\d+)/x\s*\+\s*(\d+)/x\s*\(where\s*x\s*!=\s*0\)", stmt)
        if m:
            return "easy", (int(m.group(1)), int(m.group(2)))
        m = re.fullmatch(r"Simplify:\s*(\d+)/x\s*-\s*(\d+)/\(\s*(\d+)\s*\*\s*x\s*\)\s*\(where\s*x\s*!=\s*0\)", stmt)
        if m:
            return "medium", (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m = re.fullmatch(r"Simplify:\s*(\d+)/\(\s*x\s*\+\s*(\d+)\s*\)\s*-\s*(\d+)/\(\s*x\s*\+\s*(\d+)\s*\)\s*\(where\s*x\s*!=\s*-(\d+)\s*and\s*x\s*!=\s*-(\d+)\)", stmt)
        if m:
            return "hard", (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))

    return None, None


def _build_family_texts(family: str, params: tuple) -> dict[str, str]:
    texts = {}
    if family == "easy":
        a, b = params
        statement_en = f"Simplify: {a}/x + {b}/x (where x != 0)"
        statement_si = f"සුළු කරන්න: {a}/x + {b}/x (මෙහි x != 0)"
        explanation_en = (
            f"The fractions have a common denominator x. Add the numerators: "
            f"({a} + {b})/x = {a + b}/x (where x != 0)."
        )
        explanation_si = (
            f"භාගවල පොදු හරය x වේ. හරය සමාන බැවින් ලව එකතු කරන්න: "
            f"({a} + {b})/x = {a + b}/x (මෙහි x != 0)."
        )
    elif family == "medium":
        a, b, k = params
        statement_en = f"Simplify: {a}/x - {b}/({k}*x) (where x != 0)"
        statement_si = f"සුළු කරන්න: {a}/x - {b}/({k}*x) (මෙහි x != 0)"
        explanation_en = (
            f"The least common denominator of x and {k}x is {k}x. Scale the first fraction: "
            f"({k}*{a} - {b})/({k}x) = ({k * a} - {b})/({k}x) = {k * a - b}/({k}x) (where x != 0)."
        )
        explanation_si = (
            f"x සහ {k}x හි කුඩාම පොදු ගුණාකාරය {k}x වේ. පළමු භාගය සමාන හරයකට හරවන්න: "
            f"({k}*{a} - {b})/({k}x) = ({k * a} - {b})/({k}x) = {k * a - b}/({k}x) (මෙහි x != 0)."
        )
    elif family == "hard":
        a, b, c, d = params
        lin_expr = manual._as_linear(a - c, a * d - c * b)
        statement_en = f"Simplify: {a}/(x + {b}) - {c}/(x + {d}) (where x != -{b} and x != -{d})"
        statement_si = f"සුළු කරන්න: {a}/(x + {b}) - {c}/(x + {d}) (මෙහි x != -{b} සහ x != -{d})"
        explanation_en = (
            f"The common denominator is (x + {b})(x + {d}). Expand and subtract the numerators: "
            f"[{a}(x + {d}) - {c}(x + {b})]/[(x + {b})(x + {d})] = "
            f"[{a}x + {a * d} - {c}x - {c * b}]/[(x + {b})(x + {d})] = "
            f"({lin_expr})/((x + {b})(x + {d})) (where x != -{b} and x != -{d})."
        )
        explanation_si = (
            f"පොදු හරය (x + {b})(x + {d}) වේ. ලව ප්‍රසාරණය කර අඩු කරන්න: "
            f"[{a}(x + {d}) - {c}(x + {b})]/[(x + {b})(x + {d})] = "
            f"[{a}x + {a * d} - {c}x - {c * b}]/[(x + {b})(x + {d})] = "
            f"({lin_expr})/((x + {b})(x + {d})) (මෙහි x != -{b} සහ x != -{d})."
        )
    else:
        return {}

    texts[statement_en] = statement_si
    texts[explanation_en] = explanation_si
    for prefix_en, prefix_si in PREFIXES.items():
        texts[prefix_en + explanation_en] = prefix_si + explanation_si
    return texts


def _question_texts(question) -> dict[str, str]:
    family, params = _parse_question(question)
    if not family:
        return {}
    texts = _build_family_texts(family, params)
    expl = getattr(question, "explanation", None)
    if expl and expl in texts:
        expl_si = texts[expl]
        for prefix_en, prefix_si in PREFIXES.items():
            texts[prefix_en + expl] = prefix_si + expl_si
    return texts


def _text_translation(text: str) -> str | None:
    # 1. Statement check
    m = re.fullmatch(r"Simplify:\s*(\d+)/x\s*\+\s*(\d+)/x\s*\(where\s*x\s*!=\s*0\)", text)
    if m:
        texts = _build_family_texts("easy", (int(m.group(1)), int(m.group(2))))
        return texts.get(text)
    m = re.fullmatch(r"Simplify:\s*(\d+)/x\s*-\s*(\d+)/\(\s*(\d+)\s*\*\s*x\s*\)\s*\(where\s*x\s*!=\s*0\)", text)
    if m:
        texts = _build_family_texts("medium", (int(m.group(1)), int(m.group(2)), int(m.group(3))))
        return texts.get(text)
    m = re.fullmatch(r"Simplify:\s*(\d+)/\(\s*x\s*\+\s*(\d+)\s*\)\s*-\s*(\d+)/\(\s*x\s*\+\s*(\d+)\s*\)\s*\(where\s*x\s*!=\s*-(\d+)\s*and\s*x\s*!=\s*-(\d+)\)", text)
    if m:
        texts = _build_family_texts("hard", (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))))
        return texts.get(text)

    # 2. Explanation or Feedback check
    expl_part = text
    for p_en in PREFIXES:
        if text.startswith(p_en):
            expl_part = text[len(p_en):]
            break

    # Easy explanation
    m = re.fullmatch(r"The fractions have a common denominator x\. Add the numerators: \((\d+) \+ (\d+)\)/x = (\d+)/x \(where x != 0\)\.", expl_part)
    if m:
        texts = _build_family_texts("easy", (int(m.group(1)), int(m.group(2))))
        return texts.get(text)

    # Medium explanation
    m = re.fullmatch(r"The least common denominator of x and (\d+)x is \1x\. Scale the first fraction: \(\1\*(\d+) - (\d+)\)/\(\1x\) = \((\d+) - \3\)/\(\1x\) = (\d+)/\(\1x\) \(where x != 0\)\.", expl_part)
    if m:
        texts = _build_family_texts("medium", (int(m.group(2)), int(m.group(3)), int(m.group(1))))
        return texts.get(text)

    # Hard explanation
    m = re.fullmatch(
        r"The common denominator is \(x \+ (?P<b>\d+)\)\(x \+ (?P<d>\d+)\)\. "
        r"Expand and subtract the numerators: "
        r"\[(?P<a>\d+)\(x \+ (?P=d)\) - (?P<c>\d+)\(x \+ (?P=b)\)\]/\[\(x \+ (?P=b)\)\(x \+ (?P=d)\)\] = "
        r"\[(?P=a)x \+ (?P<ad>\d+) - (?P=c)x - (?P<cb>\d+)\]/\[\(x \+ (?P=b)\)\(x \+ (?P=d)\)\] = "
        r"\((?P<lin>.+?)\)/\(\(x \+ (?P=b)\)\(x \+ (?P=d)\)\) "
        r"\(where x != -(?P=b) and x != -(?P=d)\)\.",
        expl_part
    )
    if m:
        texts = _build_family_texts("hard", (int(m.group("a")), int(m.group("b")), int(m.group("c")), int(m.group("d"))))
        return texts.get(text)

    return None


def presentation_text(field: str, text: str, question=None, misconception=None) -> str | None:
    """Topic hook for bilingual presentation.

    Returns reviewed Sinhala translation if recognized; returns None otherwise.
    Never alters mathematical expressions or canonical question data.
    """
    if field in {"recommendation", "action", "corrective_guidance", "teaching_recommendation"}:
        if text in COMMON:
            return COMMON[text]

    if text in COMMON:
        return COMMON[text]

    if question is not None:
        try:
            texts = _question_texts(question)
            if text in texts:
                return texts[text]
        except Exception:
            pass

    return _text_translation(text)
