from math import trunc

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from courses.forms import WorksheetProblemForm
from courses.maths import sn_round
from courses.models import Course, Resource, Problem, Syllabus, Worksheet
from courses.viewaids import ( course_from_kwargs, worksheet_from_kwargs,
    get_checked_problems, terminate, updated_checked_problems )


def home(request):
    context = {
        'courses': Course.objects.order_by('-school', 'nen', 'kumi'),
        'term': 3,
    }
    return render(request, 'courses/home.html', context)


def syllabus(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    syllabus = Syllabus.objects.filter(course=course).first()
    if syllabus and course.term_now: 
        lessons = terminate(syllabus)
        if 1 <= kwargs['term'] <= 4:
            lessons = lessons[kwargs['term'] - 1]
        else:
            lessons = lessons[course.term_now - 1]
    elif syllabus:
        lessons = syllabus.lesson_set.all()
    else:
        lessons = None
    context = {
        'course': course,
        'lessons': lessons,
        'syllabus': syllabus,
        'term_range': range(1, course.term_count + 1)
    }
    return render(request, 'courses/syllabus.html', context)


# Begin worksheet view functions----------------------------------------------->
def worksheets(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    active_worksheet = worksheet_from_kwargs(kwargs)
    context = {
        'course': course,
    }
    if active_worksheet:
        # get problems and update context
        active_problems = active_worksheet.problem_set.all()
        active_problem_pks = [ problem.pk for problem in active_problems ]
        randomized_problems = request.session.get('randomized_problems')
        context['is_randomized'] = 0
        if randomized_problems:
            for problem in active_problems:
                if str(problem.pk) in randomized_problems.keys():
                    problem.use_variables(randomized_problems[str(problem.pk)])
                    context['is_randomized'] = 1
        if kwargs['order'] == 'random':
            active_problems = active_problems.order_by('?')
        request.session['active_problem_pks'] = active_problem_pks
        context['active_worksheet'] = active_worksheet
        context['active_problems'] = active_problems
        context['worksheet_problem_form'] = WorksheetProblemForm()
        context['problem_order'] = kwargs['order']
    return render(request, 'courses/worksheets.html', context)


@require_POST
def worksheets_check_answer(request, *args, **kwargs) -> 'JsonResponse':
    """Update the session with user progress.

    Session keys
        checked_problems_incorrect: session key
            the primary keys of incorrectly answered problems.
        checked_problems_correct: session key
            the primary keys of correctly answered problems.

        Motivation
        The session dictionary should not be deep (`djdocs-when-sessions-are-saved`_).

    .. _djdocs-when-session-are-saved: https://docs.djangoproject.com/en/2.2/topics/http/sessions/#when-sessions-are-saved
    """
    problem = Problem.objects.filter(pk=kwargs['problem_id']).first()
    randomized_problems = request.session.get('randomized_problems')
    if randomized_problems:
        if str(problem.pk) in randomized_problems.keys():
            problem.use_variables(randomized_problems[str(problem.pk)])
    # Default response
    json_response = {
        'primary-key': problem.pk,
        'HTML_id': problem.html_id,
        'result': 'invalid form',
    }
    # split returning the result and updating the session.
    form = WorksheetProblemForm(request.POST)
    if form.is_valid():
        # Update json_response
        if problem.check_user_answer(form.cleaned_data['user_answer']):
            json_response['result'] = 'correct'
        else:
            json_response['result'] = 'incorrect'
        # Update session
        request.session['checked_problems_incorrect'] = updated_checked_problems(json_response, request.session)[0]
        request.session['checked_problems_correct'] = updated_checked_problems(json_response, request.session)[1]
    return JsonResponse(json_response)


def worksheets_check_answer_results(request, *args, **kwargs) -> 'JsonResponse':
    json_response = {
        'checked_problems_correct': get_checked_problems('correct', session=request.session),
        'checked_problems_incorrect': get_checked_problems('incorrect', session=request.session),
    }
    return JsonResponse(json_response)


def worksheets_randomize(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    worksheet = worksheet_from_kwargs(kwargs)
    course_ws_pk = '{}-{}'.format(course.pk, worksheet.pk)
    problems = worksheet_from_kwargs(kwargs).problem_set.all()
    randomized_course_ws_pks = request.session.get('randomized_course_ws_pks') or list()
    if course_ws_pk in randomized_course_ws_pks:
        # Remove the problems in the worksheet from randomized_problems
        randomized_problems = request.session.get('randomized_problems')
        for key in ( str(problem.pk) for problem in problems):
            randomized_problems.pop(key, None)
        request.session['randomized_problems'] = randomized_problems
        try:
            request.session['randomized_course_ws_pks'].remove(course_ws_pk)
        except ValueError:
            pass
    else:
        # Calculate random values for variables in problems.
        problem_vars_values = { 
            str(problem.pk): problem.variables_randomized()
            for problem in problems
            if problem.variables_as_lists
        }
        # update the session
        randomized_problems = request.session.get('randomized_problems') or dict()
        for problem_pk, variables_randomized in problem_vars_values.items():
            randomized_problems[problem_pk] = variables_randomized
        request.session['randomized_problems'] = randomized_problems
        randomized_course_ws_pks.append(course_ws_pk)
        request.session['randomized_course_ws_pks'] = randomized_course_ws_pks
    return redirect('courses:worksheets-reset', *args, **kwargs)


def worksheets_reset(request, *args, **kwargs):
    checked_problems = get_checked_problems('both', request.session)
    if any(map(len, checked_problems)):
        problem_pks = request.session['active_problem_pks']
        for pk in problem_pks:
            if pk in checked_problems[0]: checked_problems[0].remove(pk)
            if pk in checked_problems[1]: checked_problems[1].remove(pk)
        request.session['checked_problems_wrong'] = checked_problems[0]
        request.session['checked_problems_right'] = checked_problems[1]
    return redirect('courses:worksheets', *args, **kwargs)


def worksheets_reset_all(request, *args, **kwargs):
    if request.session.get('checked_problems_correct'):
        del request.session['checked_problems_correct']
    if request.session.get('checked_problems_incorrect'):
        del request.session['checked_problems_incorrect']
    return redirect('courses:worksheets', *args, **kwargs)
# END worksheet view functions ------------------------------------------------>


def resources(request, *args, **kwargs):
    course = course = course_from_kwargs(kwargs)
    context = {
        'course': course,
        'resources': course.resources,
    }
    return render(request, 'courses/resources.html', context)
