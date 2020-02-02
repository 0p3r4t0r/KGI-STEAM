from math import sin as sin_rads
from math import cos as cos_rads
from math import tan as tan_rads

# BEGIN funcitons that can be used in the forms.
from math import radians, sqrt


def sin(theta):
    return sin_rads(radians(theta))

def cos(theta):
    return cos_rads(radians(theta))

def tan(theta):
    return tan_rads(radians(theta))
# END functions that can be used in the forms.

def sn_round(number: float) -> float:
    """Round with scientific notation."""
    scientific_notation_str = '{:.2e}'.format(number)
    num_str, order_str = scientific_notation_str.split('e')
    rounded_num = round(eval(num_str), 3)
    num_str = str(rounded_num)
    scientific_notation_str = 'e'.join((num_str, order_str))
    return eval('{:.2e}'.format(number))

def sn_round_str(number: float) -> str:
    """Round with scientific notation.

    This formats long numbers so that they can be rendered in scientific
    notation in MathJax.
    """
    if number < 0.00001 or number > 100000:
        rounded = '{:.2e}'.format(number)
        value, order = rounded.split('e')
        if order.startswith('+'):
            order = order[1:].lstrip('0')
        order = '{' + order + '}'
        return '{value} \\times 10^{order}'.format(value=value, order=order)
    else:
        return str(number)
