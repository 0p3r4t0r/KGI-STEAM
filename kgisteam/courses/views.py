from math import trunc

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from courses.forms import WorksheetProblemForm
from courses.maths import sn_round
from courses.models import CATEGORY_CHOICES
from courses.models import Course, Resource, Problem, Syllabus, Worksheet
from courses.viewaids import ( course_from_kwargs, worksheet_from_kwargs,
    get_checked_problems, trimestinate, updated_checked_problems )


def courses_home(request):
    context = {
        'courses': Course.objects.order_by('-school', 'nen', 'kumi'),
    }
    return render(request, 'courses/home.html', context)


def syllabus(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    syllabus = get_object_or_404(Syllabus, course=course)
    lessons = trimestinate(syllabus)
    context = {
        'course': course,
        'lessons': lessons,
        'syllabus': syllabus,
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
        #get problems and update context
        active_problems = active_worksheet.problem_set.all()
        active_problem_pks = [ problem.pk for problem in active_problems ]
        randomized_problems = request.session.get('randomized_problems')
        if randomized_problems:
            for problem in active_problems:
                if str(problem.pk) in randomized_problems.keys():
                    problem.use_variables(randomized_problems[str(problem.pk)])
        request.session['active_problem_pks'] = active_problem_pks
        context['active_worksheet'] = active_worksheet
        context['active_problems'] = active_problems
        context['worksheet_problem_form'] = WorksheetProblemForm()
        context['problem_order'] = kwargs['order']
        context['is_randomized'] = request.session.get('is_randomized')
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

def worksheets_randomize(request, *args, **kwargs):
    is_randomized = request.session.get('is_randomized')
    problems = worksheet_from_kwargs(kwargs).problem_set.all()
    if is_randomized:
        # update the session
        randomized_problems = request.session.get('randomized_problems')
        for key in ( str(problem.pk) for problem in problems):
            randomized_problems.pop(key, None)
        request.session['randomized_problems'] = randomized_problems
        request.session['is_randomized'] = 0
    else:
        # get randomized values
        problem_vars_values = { 
            str(problem.pk): problem.variables_randomized()
            for problem in problems
            if problem.variables_lists
        }
        # update the session
        randomized_problems = request.session.get('randomized_problems') or dict()
        for problem_pk, variables_randomized in problem_vars_values.items():
            randomized_problems[problem_pk] = variables_randomized
        request.session['randomized_problems'] = randomized_problems
        request.session['is_randomized'] = 1
    return redirect('courses:worksheets', *args, **kwargs)
# END worksheet view functions ------------------------------------------------>


def resources(request, *args, **kwargs):
    course = course = course_from_kwargs(kwargs)
    context = {
        'course': course,
        'resources': course.resources,
    }
    return render(request, 'courses/resources.html', context)
