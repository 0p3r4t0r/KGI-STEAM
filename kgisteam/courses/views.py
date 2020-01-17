from copy import deepcopy
from math import trunc

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from courses.forms import WorksheetProblemForm
from courses.maths import sn_round
from courses.models import CATEGORY_CHOICES
from courses.models import Course, Resource, Problem, Syllabus, Worksheet
from courses.viewaids import course_from_kwargs, get_checked_problems, trimestinate, updated_checked_problems


def courses_home(request):
    context = {
        'courses': Course.objects.order_by('-school', 'nen', 'kumi'),
    }
    return render(request, 'courses/courses_home.html', context)


def syllabus(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    syllabus = Syllabus.objects.filter(course=course).first()
    lessons = trimestinate(syllabus)
    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'courses/course_syllabus.html', context)


# Begin worksheet view functions----------------------------------------------->
def worksheets(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    active_worksheet = course.worksheet_set.filter(
        title=kwargs['worksheet_title']
    ).first()
    context = {
        'course': course,
    }
    if active_worksheet:
        #get problems and update context
        active_problems = active_worksheet.problem_set.all()
        request.session['active_problem_pks'] = [ problem.pk for problem in active_problems ]
        context['active_worksheet'] = active_worksheet
        context['active_problems'] = active_problems
        context['worksheet_problem_form'] = WorksheetProblemForm()
        context['problem_order'] = kwargs['order']
    return render(request, 'courses/course_worksheets.html', context)


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
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_reset_all(request, *args, **kwargs):
    if request.session.get('checked_problems_correct'):
        del request.session['checked_problems_correct']
    if request.session.get('checked_problems_incorrect'):
        del request.session['checked_problems_incorrect']
    return redirect('course-worksheets', *args, **kwargs)
# END worksheet view functions ------------------------------------------------>


def resources(request, *args, **kwargs):
    course = course = course_from_kwargs(kwargs)
    context = {
        'course': course,
        'resources': course.resources,
    }
    return render(request, 'courses/course_resources.html', context)
