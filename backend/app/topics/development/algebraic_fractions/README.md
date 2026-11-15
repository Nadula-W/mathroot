# Fernando — Algebraic Fractions

This is the implementation of the `algebraic_fractions` module, covering question generation, validation, feedback, teaching recommendations, grounded answer analysis, reviewed Sinhala presentation, and remediation helpers.

---

## 1. Supported Question Families and Domain Restrictions

The topic implements three difficulty levels using bounded algebraic fraction families:

### Easy: Monomial Like-Denominator Addition
- **Expression form:**
  $$\frac{a}{x} + \frac{b}{x} = \frac{a+b}{x}$$
- **Parameters:** Integers $a, b$ satisfying $1 \le b < a \le 9$ and $a \neq 3b$.
  - The condition $a \neq 3b$ prevents the distractor $\frac{a-b}{x}$ from algebraically colliding with other options.
- **Domain restriction:** $x \neq 0$, explicitly stated in the statement and explanation (`where x != 0`).
- **Parameter space:** Exactly **33 valid distinct $(a, b)$ pairs**.

### Medium: Monomial Unlike-Denominator Subtraction
- **Expression form:**
  $$\frac{a}{x} - \frac{b}{kx} = \frac{ka - b}{kx}$$
- **Parameters:** Integers $k, a, b$ satisfying $2 \le k \le 4$ and $1 \le b < a \le 6$.
- **Domain restriction:** $x \neq 0$, explicitly stated in the statement and explanation (`where x != 0`).
- **Parameter space:** Exactly **45 valid distinct $(a, b, k)$ triples**.

### Hard: Binomial Linear Denominator Subtraction
- **Expression form:**
  $$\frac{a}{x+b} - \frac{c}{x+d} = \frac{(a-c)x + (ad - cb)}{(x+b)(x+d)}$$
- **Parameters:** Integers $a, b, c, d$ satisfying $1 \le b < d \le 6$ and $1 \le c < a \le 5$.
- **Domain restrictions:** $x \neq -b$ and $x \neq -d$, explicitly stated in the statement and explanation (`where x != -b and x != -d`).
- **Parameter space:** Exactly **150 valid distinct $(a, b, c, d)$ 4-tuples**.

---

## 2. Option Structure and Diagnostic Misconceptions

Every generated question strictly satisfies the topic contracts:
- **Option count:** Exactly four options per question.
- **Correct key:** Exactly one correct option matching `correct_expression`, validated symbolically with SymPy.
- **Pairwise distinctness:** All options are mathematically non-equivalent and checked for domain equivalence.
- **Distractors:** Exactly three distractors per question, each assigned a justified topic diagnostic code:
  - `DENOMINATOR_ADDITION`: Adding denominators directly across fractions (e.g., $\frac{a}{x} + \frac{b}{x} \to \frac{a+b}{2x}$).
  - `UNSCALED_NUMERATOR`: Converting to a common denominator without scaling the numerator.
  - `SIGN_ERROR`: Sign confusion when adding or subtracting numerators.
  - `SIGN_DISTRIBUTION_ERROR`: Failing to distribute the negative sign across a binomial numerator during subtraction.
  - `NUMERATOR_OPERATION_CONFUSION`: Multiplying numerators instead of combining via addition/subtraction.

---

## 3. Manual and AI Configuration

Configuration is managed in `ai.py` and read from environment variables. Real credentials or endpoints must never be committed; use the following placeholder structure:

```dotenv
MATHROOT_ALGEBRAIC_FRACTIONS_MODE=auto
MATHROOT_ALGEBRAIC_FRACTIONS_PROVIDER=ollama
MATHROOT_ALGEBRAIC_FRACTIONS_MODEL=qwen2.5:math
MATHROOT_ALGEBRAIC_FRACTIONS_BASE_URL=http://localhost:11434
MATHROOT_ALGEBRAIC_FRACTIONS_API_KEY=your_private_key_if_needed
MATHROOT_ALGEBRAIC_FRACTIONS_TIMEOUT_SECONDS=4
```

- **Mode:** Setting `MATHROOT_ALGEBRAIC_FRACTIONS_MODE=manual` bypasses all model calls and uses deterministic generators directly.
- **Timeouts:** Bounded by `timeout_seconds` (finite timeout between 0.1 and 60 seconds, default 4).
- **AI Question Generation:** In AI mode, the model produces only integer parameters (`a`, `b`, etc.). Python validates the parameters against family rules. All expressions, options, and explanations are assembled locally from verified deterministic templates.
- **Automatic Fallback:** Provider timeouts, connection errors, invalid JSON schemas, or out-of-range parameters raise exceptions caught by `generator.py`, which seamlessly falls back to deterministic manual question generation.

---

## 4. Grounded Answer Verification

- Implemented via `ai.analyze_answer()` and `TopicFeedbackProvider`.
- The AI selects exclusively from approved explanations and teaching recommendations passed in the context.
- The model cannot decide correctness grades, alter deterministic MCQ outcomes, or invent ungrounded misconceptions.
- Any model failure, timeout, contradictory proposed grade, or unsupported diagnostic code immediately reverts to trusted deterministic rule-based feedback.

---

## 5. Reviewed Sinhala Presentation and English Fallback

- The presentation hook `presentation_text` in `presentation.py` provides reviewed Sinhala templates for question statements, worked steps, student feedback, corrective tips, and teacher guidance across all three difficulties.
- Mathematical expressions, numbers, and variables remain untouched.
- Any unrecognized text returns `None`, allowing the presentation layer to keep the original English text and flag a translation warning.
- `validate_translation` returns `True` strictly for reviewed, approved topic wording.
- The optional dynamic translation hook returns `None` so that static reviewed templates are used reliably without exposing an unfinished dynamic provider.

---

## 6. Remediation Helpers and Scope Status

The module provides deterministic remediation algorithms to support repeated practice on misconceptions:
- `get_all_valid_parameters(difficulty)`: Enumerates all valid parameter sets for each difficulty.
- `extract_question_parameters(question)`: Bidirectionally parses parameter values from questions.
- `build_question_from_parameters(difficulty, params)`: Reconstructs validated questions from parameter tuples.
- `generate_remediation_variation(difficulty, exclude_params)`: Generates an unseen variation from the same question family, excluding previously attempted parameters.
- `ParameterSpaceExhaustedError`: Raised gracefully when all combinations in a family have been attempted.
- `generate_remediation_question(difficulty, exclude_params)`: Tries AI parameter generation, rejects parameter collisions, and falls back to manual unseen variations.

> [!NOTE]
> **Scope Notice:** Remediation helper functions and parameter deduplication algorithms are fully implemented in this module. However, shared HTTP routes (`POST /api/tests/{test_id}/answers/submit`), persistence in `mathroot_answers.verification`, and student UI rendering are part of the shared assessment system owned by Nadula and remain pending integration. Do not claim the complete end-to-end student remediation workflow is live.

---

## 7. Test Commands

Run the topic test suite from the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_algebraic_fractions.py -q -p no:cacheprovider
```

---

## 8. Unsupported and Incomplete Features

- **Topic Registration:** Registration in `backend/app/topics/__init__.py` and `PLANNED_TOPICS` (`ready: True`) is pending until Nadula performs registration.
- **Dynamic Translation Provider:** Dynamic AI translation is disabled; reviewed static templates are used.
- **End-to-End Route Remediation:** Multi-turn practice routes and state persistence belong to the shared assessment layer.
