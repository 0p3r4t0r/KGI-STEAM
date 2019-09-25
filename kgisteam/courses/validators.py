from django.forms import ValidationError
from courses.maths import sn_round, string_to_float


def validate_math_expression(math_expression: str):
    try:
        number = string_to_float(math_expression)
        sn_round(number)
    except:
        raise ValidationError('Not a number or mathematical expression.')
