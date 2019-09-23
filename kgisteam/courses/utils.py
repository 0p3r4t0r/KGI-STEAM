def sn_round(number: float) -> float:
    """Round with scientific notation."""
    return eval('{:.2e}'.format(number))

def sn_round_str(number: float) -> str:
    """Round with scientific notation."""
    if number < 0.00001 or number > 100000:
        rounded = '{:.2e}'.format(number)
        value, order = rounded.split('e')
        if order.startswith('+'):
            order = order[1:].lstrip('0')
        order = '{' + order + '}'
        return '{value} \\times 10^{order}'.format(value=value, order=order)
    else:
        return str(number)

def spaced_print(content: str) -> str:
    "just for debugging"
    spacer = '\n' * 4
    print(spacer + str(content) + spacer)
