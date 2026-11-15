# Bopage — Factors of Quadratic Expressions

Implemented as `factorization` (Factors of Quadratic Expressions). Central application registration and readiness remain pending Nadula's central integration review. The shared registry (`app/topics/__init__.py`) is kept unmodified with `factorization` unregistered and `ready: False`.

---

## 1. Supported Mathematics & Question Families

The module generates quadratic factorization multiple-choice questions across three difficulty levels:

### Easy: Monic Quadratics and Basic Difference of Two Squares
- **Monic Trinomials:** $x^2 + bx + c = (x + p)(x + q)$ where $b = p + q$ and $c = p \times q$ with integer factors $p, q > 0$.
- **Difference of Two Squares:** $x^2 - d^2 = (x - d)(x + d)$ where $d \in \{2, 3, \dots, 9\}$.
- **Mathematical guarantee:** Clean integer coefficients with no fractions.

### Medium: Monic Quadratics with Signed Coefficients
- **Signed Trinomials:** $x^2 + bx + c = (x \pm p)(x \pm q)$ covering:
  - One positive and one negative factor ($c < 0$, middle coefficient $b = p - q$ or $b = -(p - q)$).
  - Both negative factors ($c > 0$, middle coefficient $b = -(p + q)$).
- Tests sign rules for multiplication and addition of directed numbers.

### Hard: Non-Monic Quadratics and Leading Coefficient Difference of Squares
- **Non-Monic Trinomials ($a > 1$):**
  - Positive linear terms: $ax^2 + bx + c = (ax + p)(x + q)$ where $b = aq + p, c = pq$.
  - Signed linear terms: $ax^2 + bx + c = (ax - p)(x + q)$ where $b = aq - p, c = -pq$.
- **Difference of Two Squares with Leading Coefficient:**
  - $(ax)^2 - d^2 = (ax - d)(ax + d)$ where $a \in \{2, 3, 4, 5\}$ and $d \in \{1, 2, 3, 5, 7\}$.
- **Specification Diversity:** Spec generator uses over 70 distinct candidate specifications across three subtypes, ensuring varied numbers and zero duplication during repeated generation.

---

## 2. Option Structure and Diagnostic Misconceptions

Every question adheres strictly to the `InternalQuestion` contract:
- Exactly 4 unique, shuffled options with opaque UUIDs.
- Exactly one correct key (`misconception: None`), verified symbolically with SymPy.
- Exactly three distractors, each attached to an authorized diagnostic misconception:
  - `SIGN_ERROR`: Incorrect sign in factor constants, causing sign mismatch in the constant or middle coefficient.
  - `WRONG_FACTOR_PAIR`: Factor pair of the constant term chosen that does not sum to the middle coefficient.
  - `SUM_PRODUCT_CONFUSION`: Sum and product conditions confused, or coefficients directly substituted as factor constants.
  - `COEFFICIENT_FACTOR_MISALLOCATION`: Leading coefficient associated with the wrong linear factor bracket.
  - `SQUARES_SQUARE_ROOT_ERROR`: Failure to take the square root of the constant term in difference of two squares.

---

## 3. Manual and AI Operation

### Backend Environment Configuration
Topic settings are isolated under `MATHROOT_FACTORIZATION_*` and independent of other topics:

```dotenv
MATHROOT_FACTORIZATION_MODE=auto
MATHROOT_FACTORIZATION_PROVIDER=ollama
MATHROOT_FACTORIZATION_MODEL=qwen2.5:math
MATHROOT_FACTORIZATION_BASE_URL=http://127.0.0.1:11434
MATHROOT_FACTORIZATION_API_KEY=
MATHROOT_FACTORIZATION_TIMEOUT_SECONDS=4
```

- **Offline Manual Default:** Setting `MATHROOT_FACTORIZATION_MODE=manual` bypasses all network calls and runs fully offline using deterministic generators.
- **Provider Protection:** Finite timeouts (0.1–15 seconds, default 4s). No student identities, session tokens, or API credentials are ever logged or sent to the model.
- **Deterministic Validation & Fallback:** AI-proposed answer keys are never trusted blindly; `manual.validate_question()` symbolically verifies every option. Provider connection failure, timeouts, invalid JSON, or invalid mathematics trigger immediate automatic fallback to `manual.generate_question()`.

---

## 4. Grounded Answer Verification

- Implemented via `ai.analyze_answer()` and `TopicFeedbackProvider`.
- Authoritative grade is determined deterministically by matching the selected option ID against the validated key.
- The AI feedback selector selects exclusively from pre-approved explanation and corrective guidance templates in the context; it cannot override correctness grades or invent ungrounded misconceptions.

---

## 5. Reviewed Sinhala Presentation

- `presentation.py` provides complete, reviewed Sinhala translations for:
  - Question statements (`Factorize: ...` $\to$ `සාධක වෙන් කරන්න: ...`)
  - Full worked explanations across all difficulty levels and subtypes (easy trinomials, difference of squares, medium trinomials, non-monic splitting the middle term, and AI factor explanations)
  - Student misconception feedback and verification feedback
  - Teacher recommendations and corrective guidance
  - Topic title (`Factors of Quadratic Expressions` $\to$ `වර්ගජ ප්‍රකාශනවල සාධක`)
- Mathematical formulas, algebraic variables, and option identifiers are preserved without alteration.
- Unknown text safely falls back to English with a translation warning.

---

## 6. Test Suite and Verification Results

### Test Execution Command
From the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_factorization.py tests/test_factorization_ai.py -v
```

### Automated Test Results (19/19 Passed)

```text
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.2.0, pluggy-1.7.0
rootdir: mathroot\backend
plugins: anyio-4.15.1
collected 19 items

tests/test_factorization.py::test_generated_questions_are_valid PASSED   [  5%]
tests/test_factorization.py::test_exactly_one_correct_option_without_code PASSED [ 10%]
tests/test_factorization.py::test_wrong_key_is_rejected PASSED           [ 15%]
tests/test_factorization.py::test_duplicate_option_values_rejected PASSED [ 21%]
tests/test_factorization.py::test_wrong_option_without_code_rejected PASSED [ 26%]
tests/test_factorization.py::test_invalid_option_format_rejected PASSED  [ 31%]
tests/test_factorization.py::test_mismatched_expressions_rejected PASSED [ 36%]
tests/test_factorization.py::test_verify_answer PASSED                   [ 42%]
tests/test_factorization.py::test_feedback_and_recommendations PASSED    [ 47%]
tests/test_factorization.py::test_topic_adapter_and_bilingual_presentation PASSED [ 52%]
tests/test_factorization.py::test_sinhala_explanations_and_feedback_all_levels PASSED [ 57%]
tests/test_factorization_ai.py::test_good_ai_question_accepted PASSED    [ 63%]
tests/test_factorization_ai.py::test_wrong_answer_key_rejected PASSED    [ 68%]
tests/test_factorization_ai.py::test_malformed_json_raises PASSED        [ 73%]
tests/test_factorization_ai.py::test_missing_model_raises PASSED         [ 78%]
tests/test_factorization_ai.py::test_generator_fallback_when_ai_down PASSED [ 84%]
tests/test_factorization_ai.py::test_generator_fallback_when_ai_hallucinates PASSED [ 89%]
tests/test_factorization_ai.py::test_hard_ai_spec_diversity PASSED       [ 94%]
tests/test_factorization_ai.py::test_manual_mode_generation_all_levels PASSED [100%]

======================= 19 passed, 1 warning in 23.45s ========================
```

- **100+ generated questions per difficulty level** verified for algebraic equivalence, unique IDs, unique texts, and valid distractor codes.
- **Hard question diversity:** Verified over repeated runs to produce varied quadratic specifications without duplication.
- **Fallback verification:** All 3 difficulties (`easy`, `medium`, `hard`) automatically fall back to valid deterministic questions when the AI service is unreachable or returns malformed data.
- **Bilingual validation:** Verified complete Sinhala translations for worked explanations, student feedback, and full `feedback_translation` pipeline with zero missing field warnings.
