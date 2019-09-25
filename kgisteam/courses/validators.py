from django.forms import ValidationError
from courses.utils import sin, cos, tan


def validate_math_expression(math_expression: str):
    try:
        computation = eval(math_expression)
    except:
        raise ValidationError('Not a number or mathematical expression.')
