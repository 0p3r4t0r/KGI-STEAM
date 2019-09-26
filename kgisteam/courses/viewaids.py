from collections import namedtuple
from copy import deepcopy

from courses.models import Course


def course_from_kwargs(kwargs: dict) -> "<class 'courses.models.Course'>":
    """Course object from the url.

    In the data base the 'nen (year)' and 'kumi (class number/letter)'
    are stored in separate fields. In the urls, however, they have been combined
    for readability into the string 'nen-kumi'.
    """
    # Split nen-kumi into nen and kumi
    nen_kumi = kwargs['nen_kumi']
    filtered_kwargs = {
        key: value for key, value in kwargs.items()
        if key in (field.name for field in Course._meta.fields)
    }
    filtered_kwargs['nen'], filtered_kwargs['kumi'] = nen_kumi[0], nen_kumi[2]
    # Remove anything in kwargs that does not correspond to a field in Course.
    print(filtered_kwargs)
    return Course.objects.filter(**filtered_kwargs).first()

def get_checked_problems(result: str, session: 'SessionStore') -> tuple:
    """Get the primary keys of attempted problems from the session.

    When this is called with result=both the return value will be a namedtuple
    where the first element (index 0) is the incorrectly answered problems and
    the second element (index 1) is the correctly answered problems.
    """
    if result == 'correct' or result == 'incorrect':
        checked_problems = session.get('checked_problems_{}'.format(result))
        return checked_problems
    elif result == 'both':
        CheckedProblems = namedtuple('CheckedProblems', ['incorrect', 'correct'])
        checked_problems = CheckedProblems(
            session.get('checked_problems_incorrect', default=tuple()),
            session.get('checked_problems_correct', default=tuple()),
        )
        return checked_problems

def updated_checked_problems(response: dict, session: 'SessionStore') -> namedtuple:
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
    CheckedProblems = namedtuple('CheckedProblems', ['incorrect', 'correct'])
    checked_problems = CheckedProblems(
        tuple(checked_incorrect),
        tuple(checked_correct),
    )
    return checked_problems
