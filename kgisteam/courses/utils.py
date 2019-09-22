from collections import namedtuple


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

def get_checked_problems(result: str, session: 'SessionStore') -> tuple:
    if result == 'correct' or result == 'incorrect':
        checked_problems = session.get('checked_problems_{}'.format(result))
        return checked_problems
    elif result == 'both':
        CheckedProblems = namedtuple('CheckedProblems', ['incorrect', 'correct'])
        checked_problems = CheckedProblems(
            session.get('checked_problems_incorrect', default=list()),
            session.get('checked_problems_correct', default=list()),
        )
        return checked_problems

def updated_checked_problems(response: dict, session: 'SessionStore') -> tuple:
    checked_incorrect, checked_correct = get_checked_problems('both', session)
    checked_incorrect, checked_correct = set(checked_incorrect), set(checked_correct)
    result = response['result']
    pk = response['primary-key']
    if result == 'incorrect':
        checked_incorrect.add(pk)
        if pk in checked_correct: checked_correct.remove(pk)
    elif result == 'correct':
        checked_correct.add(pk)
        if pk in checked_incorrect: checked_incorrect.remove(pk)
    return (list(checked_incorrect), list(checked_correct))
