"""Sinhala templates tied to independently validated canonical questions."""
from . import manual

COMMON = {
    manual.GUIDANCE['INVERSE_SIGN']: 'එකතු කිරීම ඉවත් කිරීමට දෙපසින්ම එකම නියත පදය අඩු කරන්න.',
    manual.GUIDANCE['MISSING_DIVISION']: 'දෙපසම ඉතිරි විචල්‍ය සංගුණකයෙන් බෙදන්න.',
    manual.GUIDANCE['NEGATED_SOLUTION']: 'ධන හා ඍණ සංඛ්‍යා බෙදීම පුහුණු කර ආදේශයෙන් පිළිතුර පරීක්ෂා කරන්න.',
    manual.teaching_recommendation('unknown'): 'දෙපසටම එකම ගණිත ක්‍රියාව යොදා ආදේශයෙන් පරීක්ෂා කරන්න.',
    'Keep applying the same procedure carefully.': 'එම ක්‍රමයම සැලකිල්ලෙන් භාවිත කරන්න.',
    'Compare each step with the worked solution.': 'සෑම පියවරක්ම ලබා දී ඇති විසඳුම සමඟ සසඳන්න.',
    'Review the worked solution.': 'පියවර සහිත විසඳුම නැවත බලන්න.',
}
EVIDENCE = {
    'INVERSE_SIGN': 'නියත පදය අඩු කිරීම වෙනුවට එකතු කර තිබිය හැක.',
    'MISSING_DIVISION': 'සංගුණකයෙන් බෙදීමට පෙර නතර කර තිබිය හැක.',
    'NEGATED_SOLUTION': 'විසඳුමේ ලකුණ වෙනස් කර තිබිය හැක.',
}


def presentation_text(field, text, question=None, misconception=None):
    if text in COMMON:
        return COMMON[text]
    if question is None:
        return None
    try:
        manual.validate_question(question)
    except (ValueError, TypeError, AttributeError):
        return None
    # Replace only fixed prose in an exact, fully validated template. All
    # mathematical substrings, including spaces and signs, remain canonical.
    explanation = question.explanation
    translated = explanation
    for english, sinhala in [
        ('Collect terms: ', 'පද එක්රැස් කරන්න: '),
        ('Thus ', 'එබැවින් '),
        ('Divide both sides by ', 'දෙපසම බෙදිය යුතු අගය '),
        ('Substitution gives ', 'ආදේශයෙන් ලැබෙන අගය '),
        (' on both sides.', ' දෙපසටම ලැබේ.'),
    ]:
        translated = translated.replace(english, sinhala)
    texts = {
        question.statement: f'x සඳහා විසඳන්න: {question.source_expression}',
        explanation: translated,
        'Correct. ' + explanation: 'නිවැරදියි. ' + translated,
        'Incorrect answer. ' + explanation: 'පිළිතුර වැරදියි. ' + translated,
        'Review your working. ' + explanation: 'ඔබේ විසඳුම නැවත පරීක්ෂා කරන්න. ' + translated,
    }
    for code, evidence in manual.MISCONCEPTIONS.items():
        texts[f'Possible misconception: {evidence} ' + explanation] = (
            'ඇති විය හැකි වැරදි අවබෝධය: ' + EVIDENCE[code] + ' ' + translated
        )
    return texts.get(text)


def validate_translation(field, source, translated, question=None):
    expected = presentation_text(field, source, question=question)
    return expected is not None and translated == expected
