def sn_round(number: float) -> float:
    """Round with scientific notation."""
    return eval('{:.2e}'.format(number))

def sn_round_str(number: float) -> str:
    """Round with scientific notation."""
    rounded = '{:.2e}'.format(number)
    value, order = rounded.split('e')
    if order.startswith('+'):
        order = order[1:].lstrip('0')
    order = '{' + order + '}'
    return '{value} \\times 10^{order}'.format(value=value, order=order)
