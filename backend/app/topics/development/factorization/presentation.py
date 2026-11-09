"""Reviewed Sinhala presentation for factorization templates.

This module never generates a question or changes an answer. Unknown historical
wording is deliberately left to the shared, fail-closed presentation fallback.
"""
import re
from .manual import MISCONCEPTIONS

RECOMMENDATIONS = {
    "SIGN_ERROR": (
        "Review multiplication and addition of directed numbers, then practice factorizing quadratics with negative coefficients.",
        "ලකුණු සහිත සංඛ්‍යා ගුණ කිරීම හා එකතු කිරීම නැවත ආවර්ජනය කර, ඍණ සංගුණක සහිත වර්ගජ ප්‍රකාශන සාධක කැඩීම පුහුණු වන්න.",
    ),
    "WRONG_FACTOR_PAIR": (
        "List all integer factor pairs of the constant term and check their sums systematically before writing factors.",
        "නියත පදයේ සියලු සාධක යුගල ලියා, ඒවායේ එකතුව මැද පදයේ සංගුණකයට සමාන වේදැයි ක්‍රමානුකූලව පරීක්ෂා කරන්න.",
    ),
    "SUM_PRODUCT_CONFUSION": (
        "Emphasize that the factor constants must MULTIPLY to the constant term 'c' and ADD to the middle coefficient 'b'.",
        "සාධකවල නියත පද දෙකෙහි ගුණිතය අවසාන පදයටත්, එකතුව මැද පදයේ සංගුණකයටත් සමාන විය යුතු බව සිහිපත් කරන්න.",
    ),
    "COEFFICIENT_FACTOR_MISALLOCATION": (
        "When factorizing ax^2 + bx + c, use splitting the middle term and factor by grouping to place coefficients correctly.",
        "ax^2 + bx + c ආකාරයේ ප්‍රකාශනවල මැද පදය වෙන් කර, පද කාණ්ඩ කර සාධක ගැනීමේ ක්‍රමය භාවිත කරන්න.",
    ),
    "SQUARES_SQUARE_ROOT_ERROR": (
        "Review the difference of two squares rule a^2 - b^2 = (a - b)(a + b), identifying the square roots of both terms.",
        "වර්ග දෙකක අන්තරය a^2 - b^2 = (a - b)(a + b) සූත්‍රය භාවිතයේදී පද දෙකෙහි වර්ගමූල නිවැරදිව හඳුනා ගන්න.",
    ),
}

COMMON = {
    "Factors of Quadratic Expressions": "වර්ගජ ප්‍රකාශනවල සාධක",
    "Review quadratic factorization with another worked example.": "තවත් පියවර සහිත උදාහරණයකින් වර්ගජ ප්‍රකාශන සාධක වෙන් කිරීම නැවත බලන්න.",
    "Check that the product of the constants equals the last term and their sum gives the middle coefficient upon expansion.": "ප්‍රසාරණය කිරීමේදී නියත පදවල ගුණිතය අවසාන පදයටත්, එකතුව මැද පදයේ සංගුණකයටත් සමාන වේදැයි පරීක්ෂා කරන්න.",
    "Keep applying the same procedure carefully.": "එම ක්‍රමයම සැලකිල්ලෙන් භාවිත කරන්න.",
    "Compare each step with the worked solution.": "ඔබේ එක් එක් පියවර විසඳුමේ අදාළ පියවර සමඟ සසඳන්න.",
    "Review the worked solution.": "පියවර සහිත විසඳුම නැවත බලන්න.",
    "Review quadratic factorization steps.": "වර්ගජ ප්‍රකාශන සාධක වෙන් කිරීමේ පියවර නැවත බලන්න.",
    "Incorrect answer. The selection alone does not establish a particular misconception.": "පිළිතුර වැරදියි. තෝරාගත් පිළිතුර පමණක් මත නිශ්චිත වැරදි අවබෝධයක් තහවුරු කළ නොහැක.",
    "Correct answer. All terms and signs match the quadratic expression.": "පිළිතුර නිවැරදියි. සියලු පද සහ ලකුණු වර්ගජ ප්‍රකාශනය සමඟ ගැළපේ.",
}
COMMON.update(dict(RECOMMENDATIONS.values()))

MISCONCEPTION_TRANSLATIONS = {
    "A factor has an incorrect sign, resulting in an incorrect middle term or constant.": "සාධකයක ලකුණ වැරදී ඇති නිසා මැද පදය හෝ නියත පදය වැරදී ඇත.",
    "Selected a factor pair of the constant term that does not sum to the middle coefficient.": "නියත පදයේ සාධක යුගලක් තෝරාගෙන ඇති නමුත් එහි එකතුව මැද පදයේ සංගුණකයට සමාන නොවේ.",
    "Confused the sum and product of the roots, or directly used coefficients as factor terms.": "මූලයන්ගේ එකතුව සහ ගුණිතය පටලවා ගෙන හෝ සංගුණක කෙලින්ම සාධක ලෙස භාවිත කර ඇත.",
    "Associated the leading coefficient with the wrong linear factor.": "ප්‍රධාන සංගුණකය වැරදි රේඛීය සාධකයට සම්බන්ධ කර ඇත.",
    "Failed to take the square root of the constant term in a difference of two squares.": "වර්ග දෙකක අන්තරයේදී නියත පදයේ වර්ගමූලය ගැනීමට අසමත් වී ඇත.",
}
COMMON.update(MISCONCEPTION_TRANSLATIONS)

PREFIXES = {
    "Correct. You identified the correct factors of the quadratic expression. ": "නිවැරදියි. ඔබ වර්ගජ ප්‍රකාශනයේ නිවැරදි සාධක හඳුනාගෙන ඇත. ",
    "You may have made a sign error when finding the factor pair or signs. Review signed multiplication and addition. ": "සාධක යුගල හෝ ලකුණු සෙවීමේදී ලකුණු දෝෂයක් සිදුවී තිබිය හැක. ධන හා ඍණ සංඛ්‍යා ගුණ කිරීම හා එකතු කිරීම නැවත බලන්න. ",
    "You selected factors that multiply to the constant term but do not add to the middle term coefficient. ": "ඔබ තෝරාගත් සාධකවල ගුණිතය නියත පදයට සමාන වුවද, ඒවායේ එකතුව මැද පදයේ සංගුණකයට සමාන නොවේ. ",
    "You may have confused the sum and product of the terms, or directly used coefficients as factor constants. ": "ඔබ පදවල එකතුව සහ ගුණිතය පටලවා ගෙන හෝ සංගුණක කෙලින්ම සාධක ලෙස භාවිත කර තිබිය හැක. ",
    "You associated the leading coefficient with the wrong factor, altering the middle term upon expansion. ": "ඔබ ප්‍රධාන සංගුණකය වැරදි සාධකයට සම්බන්ධ කිරීම නිසා ප්‍රසාරණයේදී මැද පදය වෙනස් වේ. ",
    "In a difference of two squares, remember to take the square root of the constant term. ": "වර්ග දෙකක අන්තරයේදී, නියත පදයේ වර්ගමූලය ගැනීමට මතක තබා ගන්න. ",
    "Review quadratic factorization steps. ": "වර්ගජ ප්‍රකාශන සාධක වෙන් කිරීමේ පියවර නැවත බලන්න. ",
    "Incorrect answer. ": "පිළිතුර වැරදියි. ",
    "Correct answer. All terms and signs match the quadratic expression. ": "පිළිතුර නිවැරදියි. සියලු පද සහ ලකුණු වර්ගජ ප්‍රකාශනය සමඟ ගැළපේ. ",
    "Possible misconception: a sign error in the factors causing an incorrect middle term or constant. ": "ඇති විය හැකි වැරදි අවබෝධය: සාධකවල ලකුණු දෝෂයක් නිසා මැද පදය හෝ නියත පදය වැරදී යාම. ",
    "Possible misconception: choosing a factor pair that satisfies the product but not the required sum. ": "ඇති විය හැකි වැරදි අවබෝධය: ගුණිතය ගැළපුණද අවශ්‍ය එකතුව නොලැබෙන සාධක යුගලක් තෝරා ගැනීම. ",
    "Possible misconception: confusing the sum and product conditions for quadratic factorization. ": "ඇති විය හැකි වැරදි අවබෝධය: වර්ගජ සාධක වෙන් කිරීමේදී එකතුව සහ ගුණිතය පටලවා ගැනීම. ",
    "Possible misconception: placing the leading coefficient in the wrong linear bracket. ": "ඇති විය හැකි වැරදි අවබෝධය: ප්‍රධාන සංගුණකය වැරදි වරහන තුළට යෙදීම. ",
    "Possible misconception: using the square instead of the square root in a difference of two squares. ": "ඇති විය හැකි වැරදි අවබෝධය: වර්ග දෙකක අන්තරයේදී වර්ගමූලය වෙනුවට වර්ගයම භාවිත කිරීම. ",
    "Incorrect answer. The selection alone does not establish a particular misconception. ": "පිළිතුර වැරදියි. තෝරාගත් පිළිතුර පමණක් මත නිශ්චිත වැරදි අවබෝධයක් තහවුරු කළ නොහැක. ",
}


def _translate_explanation(expl: str) -> str | None:
    """Deterministically translate mathematical factorization explanations to Sinhala."""
    if not expl:
        return None
    expl = expl.strip()

    # 1. Easy trinomial: "Find two numbers that multiply to {c} and add to {b}: {p} × {q} = {c} and {p} + {q} = {b}. The factors are {factors}."
    m = re.fullmatch(
        r"Find two numbers that multiply to (-?\d+) and add to (-?\d+):\s*(.+?)\s*=\s*(-?\d+)\s+and\s+(.+?)\s*=\s*(-?\d+)\.\s+The factors are (.+)\.",
        expl,
    )
    if m:
        c, b, p_times_q, prod, p_plus_q, sum_, factors = m.groups()
        return f"ගුණිතය {c} සහ එකතුව {b} වන සංඛ්‍යා දෙක සොයන්න: {p_times_q} = {prod} සහ {p_plus_q} = {sum_}. සාධක වන්නේ {factors} වේ."

    # 2. Easy difference of squares: "Apply the difference of two squares identity a^2 - b^2 = (a - b)(a + b): x^2 - {d}^2 = {factors}."
    m = re.fullmatch(
        r"Apply the difference of two squares identity a\^2 - b\^2 = \(a - b\)\(a \+ b\):\s*x\^2\s*-\s*(\d+)\^2\s*=\s*(.+)\.",
        expl,
    )
    if m:
        d, factors = m.groups()
        return f"වර්ග දෙකක අන්තරය a^2 - b^2 = (a - b)(a + b) සූත්‍රය භාවිත කරන්න: x^2 - {d}^2 = {factors}."

    # 3. Medium trinomial: "Find two numbers that multiply to {c} and add to {b}. The required factors are {factors}."
    m = re.fullmatch(
        r"Find two numbers that multiply to (-?\d+) and add to (-?\d+)\.\s+The required factors are (.+)\.",
        expl,
    )
    if m:
        c, b, factors = m.groups()
        return f"ගුණිතය {c} සහ එකතුව {b} වන සංඛ්‍යා දෙක සොයන්න. අවශ්‍ය සාධක වන්නේ {factors} වේ."

    # 4. Hard non-monic splitting middle term: "Split the middle term {bx} into {px} and {aqx}: {expr} = {factors}."
    m = re.fullmatch(
        r"Split the middle term (-?\w+) into (-?\w+) and (-?\w+):\s*(.+?)\s*=\s*(.+)\.",
        expl,
    )
    if m:
        bx, px, aqx, expr, factors = m.groups()
        return f"මැද පදය වන {bx}, {px} සහ {aqx} ලෙස වෙන් කරන්න: {expr} = {factors}."

    # 5. Hard difference of squares with coefficient: "Apply the difference of two squares identity: ({ax})^2 - {d}^2 = {factors}."
    m = re.fullmatch(
        r"Apply the difference of two squares identity:\s*\((.+?)\)\^2\s*-\s*(\d+)\^2\s*=\s*(.+)\.",
        expl,
    )
    if m:
        ax, d, factors = m.groups()
        return f"වර්ග දෙකක අන්තරය සූත්‍රය භාවිත කරන්න: ({ax})^2 - {d}^2 = {factors}."

    # 6. AI explanation: "The factors are {factors}."
    m = re.fullmatch(r"The factors are (.+)\.", expl)
    if m:
        factors = m.group(1)
        return f"සාධක වන්නේ {factors} වේ."

    return None


def _question_texts(question) -> dict[str, str]:
    texts = {}
    stmt = question.statement
    if stmt.startswith("Factorize: "):
        expr_part = stmt[len("Factorize: "):]
        texts[stmt] = f"සාධක වෙන් කරන්න: {expr_part}"

    expl = question.explanation
    si_expl = _translate_explanation(expl)
    effective_expl = si_expl if si_expl is not None else expl
    texts[expl] = effective_expl

    for prefix, translated in PREFIXES.items():
        texts[prefix + expl] = translated + effective_expl
    return texts


def presentation_text(field: str, text: str, question=None, misconception=None) -> str | None:
    """Optional topic hook. Matching full text avoids unsafe substring replacement."""
    if field in {"recommendation", "action", "corrective_guidance", "teaching_recommendation", "misconception", "title"}:
        if text in COMMON:
            return COMMON[text]
    if question is not None:
        try:
            val = _question_texts(question).get(text)
            if val is not None:
                return val
        except (ValueError, SyntaxError, TypeError):
            pass
    if text in COMMON:
        return COMMON[text]
    if text.startswith("Factorize: "):
        return f"සාධක වෙන් කරන්න: {text[len('Factorize: '):]}"
    si_expl = _translate_explanation(text)
    if si_expl is not None:
        return si_expl
    for prefix, translated in PREFIXES.items():
        if text.startswith(prefix):
            rest = text[len(prefix):]
            rest_tr = _translate_explanation(rest)
            if rest_tr is not None:
                return translated + rest_tr
            return translated + rest
    return None
