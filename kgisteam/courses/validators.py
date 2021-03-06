from django.forms import ValidationError
from courses.maths import evaluate_answer, sn_round


def validate_math_expression(math_expression: str):
    try:
        number = evaluate_answer(math_expression)
        sn_round(number)
    except:
        raise ValidationError('Not a number or mathematical expression.')
