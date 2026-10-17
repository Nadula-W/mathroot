
import random #Select different numbers for new questions
from uuid import uuid4 #to generate unique IDs for answer options
from sympy import Symbol, expand, simplify

from app.contracts import InternalQuestion, InternalOption

x = Symbol('x') #This creates an algebraic variable named

#to make mathematical expressions readable
def _as_text(coefficient: int, constant: int) -> str:
    """Format `coefficient*x + constant` as friendly algebra."""
    if coefficient == 0:
        x_part = ''
    elif coefficient == 1:
        x_part = 'x'
    elif coefficient == -1:
        x_part = '-x'
    else:
        x_part = f'{coefficient}x'
    if constant == 0:
        return x_part or '0'
    if not x_part:
        return str(constant)
    
    sign = '+' if constant > 0 else '-'
    return f'{x_part} {sign} {abs(constant)}' #abs(constant) obtains the absolute value, preventing expressions such as 3x - -5


class BinomialTopic:
    topic_id = 'binomial'
    title = 'Grade 10 — Binomial Expressions'

#init runs when an object is created
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.SystemRandom()

    def generate_question(self, difficulty: str) -> InternalQuestion:
        if difficulty not in {'easy', 'medium', 'hard'}:
            raise ValueError('Difficulty must be easy, medium, or hard.')
        
        if difficulty == 'easy':
            a = self.rng.randint(2, 6)
            b = self.rng.randint(2, 9)
        elif difficulty == 'medium':
            a = self.rng.randint(2, 7)
            b = -self.rng.randint(2, 9)
        else:
            a = -self.rng.randint(2, 7)
            b = self.rng.choice([-1, 1]) * self.rng.randint(2, 9)

        statement = f"Expand and simplify: {a}({('x + ' + str(b)) if b >= 0 else ('x - ' + str(abs(b)))})"
        expected = expand(a * (x + b))

        # Each incorrect option is deliberately connected to a meaningful error.
        raw_options = [
            ('correct', a * x + a * b, None),
            ('wrong_constant', a * x + b, 'DISTRIBUTION_CONSTANT'),
            ('wrong_variable', x + a * b, 'DISTRIBUTION_VARIABLE'),
            ('wrong_sign', a * x - a * b, 'SIGN_ERROR'),
        ]

        # Recalculate equivalence with SymPy rather than trusting the LLM or templates.
        for idx, (_, expression, _) in enumerate(raw_options):

            if (simplify(expression - expected) == 0) != (idx == 0): #checks if the expression is equivalent to the expected answer and its index is 0 (the correct answer)
                raise ValueError('Generated an invalid distractor or answer.')
            
            for other_idx in range(idx):
                if simplify(expression - raw_options[other_idx][1]) == 0: #This checks whether the current answer is the same as any previous answer.
                    raise ValueError('Generated duplicate answer options.')

        # unique IDs prevent student clients from reading answer semantics.
        correct_option_id = str(uuid4()) #str() converts the UUID object into a string.
        
        identified = [
            (correct_option_id if label is None else str(uuid4()), expr, label)
            for _, expr, label in raw_options
        ]
        self.rng.shuffle(identified) #The .shuffle() method randomly changes the order of items inside a list
        options = [
            InternalOption(id=option_id,
            # Convert the SymPy expression into a student-friendly mathematical string.
            # expr.coeff(x) extracts the coefficient of x (e.g., 3 from 3*x + 12).
            # expr.subs(x, 0) substitutes x = 0 to extract the constant term (e.g., 12).
            # int() converts both SymPy values into Python integers.
            # _as_text(3, 12) formats these values as "3x + 12" instead of "3*x + 12".

            text=_as_text(int(expr.coeff(x)), int(expr.subs(x, 0))),
                            text=_as_text(int(expr.coeff(x)),int(expr.subs(x, 0))), 
                            misconception=label)
            for option_id, expr, label in identified
        ]

        answer_text = _as_text(a, a * b)
        explanation = ( #An f-string lets you insert variable values inside a string using curly braces.
            f'Distribute {a} to BOTH terms: '
            f'{a} × x = {_as_text(a, 0)} '
            f'and {a} × ({b}) = {a * b}. '
            f'The answer is {answer_text}.'
        )
    #ex- Distribute 3 to BOTH terms: (3\times x=3x\)(3\times4=12\)Therefore, the answer is \(3x+12\).
        return InternalQuestion(
            id=str(uuid4()),
            topic_id=self.topic_id,
            difficulty=difficulty,
            statement=statement,
            options=options,
            correct_option_id=correct_option_id,
            explanation=explanation,
            source_expression=f'{a}*(x+({b}))',
            correct_expression=str(expected),
        )

    def feedback(self, question: InternalQuestion, misconception: str | None) -> str:
        if misconception is None:
            return 'Correct. You distributed multiplication to both terms. ' + question.explanation
        messages = {
            'DISTRIBUTION_CONSTANT': 'You may have multiplied the x term but forgotten to multiply the constant. ',
            'DISTRIBUTION_VARIABLE': 'You may have multiplied the constant but forgotten to multiply the x term. ',
            'SIGN_ERROR': 'You may have changed a sign when multiplying the constant. Review multiplication with negative numbers. ',
        }
        return messages.get(misconception, 'Review the distributive law. ') + question.explanation

    def teaching_recommendation(self, misconception: str) -> str:
        recommendations = {
            'DISTRIBUTION_CONSTANT': 'Demonstrate how the outside coefficient multiplies BOTH bracket terms, then assign two expansion examples.',
            'DISTRIBUTION_VARIABLE': 'Review multiplication of coefficients and variables before expanding brackets.',
            'SIGN_ERROR': 'Revisit signed-number multiplication, then practise bracket expansion with negative constants.',
        }
        return recommendations.get(misconception, 'Review expansion of brackets with another worked example.')
