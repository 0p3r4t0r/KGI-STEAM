from django.forms import ValidationError


def validate_math_expression(math_expression: str):
    try:
        computation = eval(math_expression)
    except:
        raise ValidationError('Not a number or mathematical expression.')
