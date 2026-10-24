"""Presentation invariants and hybrid translation guards; no live provider/DB."""
import json
import random
import re
from dataclasses import asdict, replace

import httpx
import pytest

from app import presentation
from app.answer_verification import Analysis, verify_answer
from app.presentation import (
    OllamaTranslationProvider, feedback_translation, mask_math,
    question_translation, recommendation_translation, restore_translation,
)
from app.topics.development.binomial.generator import LLMBinomialTopic
from app.topics.development.binomial.manual import BinomialTopic


@pytest.fixture(autouse=True)
def clear_translation_cache():
    presentation._CACHE.clear()
    yield
    presentation._CACHE.clear()


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_reviewed_question_translation_preserves_all_math_and_ids(difficulty):
    topic = BinomialTopic(random.Random(23))
    for _ in range(5):
        question = topic.generate_question(difficulty)
        before = asdict(question)
        metadata = question_translation(question, topic)
        assert metadata['translation_warnings'] == []
        assert metadata['translations']['si']['statement'] == question.statement.replace(
            'Expand and simplify: ', 'ප්‍රසාරණය කර සුළු කරන්න: ', 1,
        )
        assert set(metadata['translations']['si']) == {'statement'}
        assert asdict(question) == before
        assert not any(secret in json.dumps(metadata) for secret in ('correct_option_id', 'explanation', 'misconception'))


@pytest.mark.parametrize('code', [None, 'DISTRIBUTION_CONSTANT', 'DISTRIBUTION_VARIABLE', 'SIGN_ERROR'])
@pytest.mark.parametrize('ai_assisted', [False, True])
def test_manual_and_grounded_ai_feedback_translate_without_translation_service(monkeypatch, code, ai_assisted):
    topic = BinomialTopic(random.Random(4))
    question = topic.generate_question('hard')
    option = next(option for option in question.options if option.misconception == code)
    monkeypatch.setenv('MATHROOT_ANSWER_VERIFIER', 'auto' if ai_assisted else 'manual')
    class Grounded:
        def analyze(self, context):
            return Analysis(proposed_correct=context['verified_correct'],
                            explanation=context['approved_explanations'][-1],
                            suspected_misconception=context['supported_misconception'],
                            confidence=0.99, corrective_guidance=context['approved_guidance'][-1])
    result = verify_answer(question, option.id, topic, Grounded())
    before = result.copy()
    monkeypatch.setattr(topic, 'translation_provider', lambda: pytest.fail('Reviewed fallback called AI translation'))
    translated = feedback_translation(question, {'statement': question.statement, **result}, topic)
    assert translated['translation_warnings'] == []
    texts = translated['translations']['si']
    assert all(field in texts for field in ('statement', 'explanation', 'feedback', 'corrective_guidance', 'teaching_recommendation'))
    assert result == before and result['correct'] == (code is None)
    assert texts['explanation'] in texts['feedback']


def test_existing_ollama_generated_template_and_negative_coefficients_translate(monkeypatch):
    from app.topics.development.binomial import generator
    class Response:
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def read(self): return json.dumps({'message': {'content': json.dumps({'outer': -3, 'inner_x': 4, 'constant': -5})}}).encode()
    monkeypatch.setattr(generator, 'urlopen', lambda *_args, **_kwargs: Response())
    topic = LLMBinomialTopic(random.Random(2))
    question = topic._generate_using_ollama('hard')
    translated = feedback_translation(question, {'statement': question.statement, 'explanation': question.explanation}, topic)
    assert translated['translation_warnings'] == []
    assert translated['translations']['si']['statement'].endswith('-3(4x - 5)')
    for expression in ('-3 × (4x) = -12x', '-3 × (-5) = 15', '-12x + 15'):
        assert expression in translated['translations']['si']['explanation']


@pytest.mark.parametrize('code', list(BinomialTopic.misconception_definitions))
def test_teacher_recommendation_uses_reviewed_wording(code):
    topic = BinomialTopic()
    text = topic.teaching_recommendation(code)
    metadata = recommendation_translation(topic, code, text)
    assert metadata['translation_warnings'] == []
    assert metadata['translations']['si']['recommendation'] == metadata['translations']['si']['action']


def test_unknown_historical_wording_retains_english_with_warning(monkeypatch):
    monkeypatch.setenv('MATHROOT_TRANSLATION_MODE', 'manual')
    topic = BinomialTopic()
    question = replace(topic.generate_question('easy'), statement='Expand a mystery expression.', explanation='A historical custom explanation.')
    metadata = feedback_translation(question, {'statement': question.statement, 'explanation': question.explanation}, topic)
    assert metadata['translations']['si'] == {}
    assert metadata['translation_warnings'] == ['statement', 'explanation']
    assert question.statement == 'Expand a mystery expression.'


def test_inconsistent_historical_math_is_not_translated():
    topic = BinomialTopic()
    question = replace(topic.generate_question('easy'), correct_expression='999*x')
    metadata = question_translation(question, topic)
    assert 'statement' in metadata['translation_warnings']
    assert 'statement' not in metadata['translations']['si']


def test_masking_keeps_complete_formula_spacing_and_latex():
    source = 'Expand 3(x + 4), compare x² and $y+2$.'
    masked, fragments = mask_math(source)
    assert fragments == ['3(x + 4)', 'x²', '$y+2$']
    translated = 'ප්‍රසාරණය කරන්න: [[MATH_0]], සසඳන්න [[MATH_1]] සහ [[MATH_2]].'
    restored = restore_translation(translated, fragments)
    assert all(fragment in restored for fragment in fragments)
    assert '3(x + 4)' not in masked


@pytest.mark.parametrize('bad', [
    'සුළු කරන්න: [[MATH_0]] සහ [[MATH_0]].',
    'සුළු කරන්න: [[MATH_1]] සහ [[MATH_0]].',
    'සුළු කරන්න.',
    'සුළු කරන්න: [[MATH_0]] සහ [[MATH_1]] = 999.',
    'Translate [[MATH_0]] and [[MATH_1]].',
    'සුළු කරන්න: [[MATH_0]] සහ [[MATH_1]] + y.',
    'සුළු කරන්න: [[MATH_0]] සහ [[MATH_1]] ෧.',
    '<script>සුළු කරන්න: [[MATH_0]] සහ [[MATH_1]].</script>',
])
def test_unsafe_translation_is_rejected(bad):
    with pytest.raises(ValueError):
        restore_translation(bad, ['3(x + 4)', '2x'])


class CustomTopic:
    topic_id = 'custom'
    def __init__(self, approve=True, error=None):
        self.calls, self.approve, self.error = 0, approve, error
    def translation_provider(self):
        return self
    def translate(self, text):
        self.calls += 1
        if self.error:
            raise self.error
        return 'සුළු කරන්න: ' + ' සහ '.join(re.findall(r'\[\[MATH_\d+\]\]', text)) + '.'
    def validate_translation(self, field, source, translated, question=None):
        # This test topic recognizes a single reviewed semantic pair.
        return self.approve and source == 'Simplify 3(x + 4).' and translated == 'සුළු කරන්න: 3(x + 4).'


def test_dynamic_provider_requires_semantic_approval_and_reuses_validated_cache():
    topic = CustomTopic()
    text = 'Simplify 3(x + 4).'
    for _ in range(2):
        metadata = recommendation_translation(topic, 'EXAMPLE', text)
        assert metadata['translation_warnings'] == []
        assert metadata['translations']['si']['recommendation'] == 'සුළු කරන්න: 3(x + 4).'
    assert topic.calls == 1
    topic.approve = False
    rejected = recommendation_translation(topic, 'EXAMPLE', text)
    assert rejected['translations']['si'] == {} and rejected['translation_warnings'] == ['recommendation']


def test_structural_math_checks_alone_do_not_approve_ai_translation():
    topic = CustomTopic(approve=False)
    result = recommendation_translation(topic, 'EXAMPLE', 'Simplify 3(x + 4).')
    assert result['translation_warnings'] == ['recommendation']
    assert result['translations']['si'] == {}


@pytest.mark.parametrize('error', [httpx.ReadTimeout('slow'), httpx.ConnectError('offline'), ValueError('invalid JSON')])
def test_dynamic_provider_failure_retains_original_english(error):
    topic = CustomTopic(error=error)
    result = recommendation_translation(topic, 'EXAMPLE', 'Simplify 3(x + 4).')
    assert result['translations']['si'] == {} and result['translation_warnings'] == ['recommendation']


def test_absent_topic_validator_skips_provider_entirely():
    topic = CustomTopic()
    topic.validate_translation = None
    result = recommendation_translation(topic, 'EXAMPLE', 'Simplify 3(x + 4).')
    assert result['translation_warnings'] == ['recommendation'] and topic.calls == 0


def test_provider_calls_are_bounded_per_metadata_object():
    topic = CustomTopic()
    question = BinomialTopic().generate_question('easy')
    detail = {field: 'Unreviewed dynamic prose.' for field in ('statement', 'explanation', 'feedback', 'corrective_guidance')}
    result = feedback_translation(question, detail, topic)
    assert len(result['translation_warnings']) == 4 and topic.calls == 2


def test_nonmathematical_options_keep_ids_and_order():
    topic = CustomTopic()
    question = BinomialTopic().generate_question('easy')
    question = replace(question, options=[replace(option, text='Simplify 3(x + 4).') for option in question.options])
    metadata = question_translation(question, topic)
    options = metadata['translations']['si']['options']
    assert [option['id'] for option in options] == [option.id for option in question.options]
    assert all(option['text'] == 'සුළු කරන්න: 3(x + 4).' for option in options)


@pytest.mark.parametrize('timeout,expected', [('0.5', 0.5), ('999', 2), ('nan', 2), ('bad', 2)])
def test_actual_ollama_adapter_timeout_and_schema(monkeypatch, timeout, expected):
    monkeypatch.setenv('MATHROOT_TRANSLATION_MODE', 'auto')
    monkeypatch.setenv('MATHROOT_TRANSLATION_TIMEOUT_SECONDS', timeout)
    monkeypatch.setenv('MATHROOT_TRANSLATION_MODEL', 'independent-translation-model')
    def post(self, url, **kwargs):
        assert self.timeout.read == expected
        assert kwargs['json']['model'] == 'independent-translation-model'
        context = json.loads(kwargs['json']['messages'][1]['content'])
        assert set(context) == {'text'} and '[[MATH_0]]' in context['text']
        return httpx.Response(200, request=httpx.Request('POST', url), json={'message': {'content': json.dumps({'text': 'සුළු කරන්න: [[MATH_0]].'})}})
    monkeypatch.setattr(httpx.Client, 'post', post)
    provider = OllamaTranslationProvider()
    assert provider.translate('Simplify [[MATH_0]].') == 'සුළු කරන්න: [[MATH_0]].'


def test_default_ollama_translation_mode_makes_no_request(monkeypatch):
    monkeypatch.delenv('MATHROOT_TRANSLATION_MODE', raising=False)
    monkeypatch.setattr(httpx.Client, 'post', lambda *_args, **_kwargs: pytest.fail('Unexpected request'))
    with pytest.raises(RuntimeError):
        OllamaTranslationProvider().translate('Unreviewed prose.')


@pytest.mark.parametrize('content', ['not JSON', '{}', '{"text": true}', '{"text": "anything", "extra": 1}'])
def test_ollama_adapter_rejects_invalid_json_and_schema(monkeypatch, content):
    monkeypatch.setenv('MATHROOT_TRANSLATION_MODE', 'auto')
    def post(self, url, **_kwargs):
        return httpx.Response(200, request=httpx.Request('POST', url), json={'message': {'content': content}})
    monkeypatch.setattr(httpx.Client, 'post', post)
    with pytest.raises(ValueError):
        OllamaTranslationProvider().translate('Simplify [[MATH_0]].')
