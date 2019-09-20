from copy import deepcopy
from math import trunc

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from courses.forms import WorksheetProblemForm
from courses.models import CATEGORY_CHOICES
from courses.models import Course, CourseResource, Problem, SharedResource, Syllabus, Worksheet
from courses.utils import sn_round


def courses_home(request):
    context = {
        'courses': Course.objects.order_by('-school', 'nen', 'kumi'),
    }
    return render(request, 'courses/courses_home.html', context)


# Roughly refactored
def course_from_kwargs(kwargs):
    filter_kwargs = deepcopy(kwargs)
    # Split nen-kumi into nen and kumi
    nen_kumi = kwargs['nen_kumi']
    filter_kwargs['nen'], filter_kwargs['kumi'] = nen_kumi[0], nen_kumi[2]
    # Remove anything in kwargs that does not correspond to a field in Course.
    filter_kwargs = {
        key: value for key, value in kwargs.items()
        if key in (field.name for field in Course._meta.fields)
    }
    return Course.objects.filter(**filter_kwargs).first()


def syllabus(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    syllabus = Syllabus.objects.filter(course=course).first()
    context = {
        'course': course,
        'syllabus': syllabus,
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
        context['active_worksheet'] = active_worksheet
        context['active_problems'] = active_problems
        context['worksheet_problem_form'] = WorksheetProblemForm()
        context['problem_order'] = kwargs['order']
        context['checked_problems'] = request.session.get('checked_problems')
    return render(request, 'courses/course_worksheets.html', context)


@require_POST
def worksheets_check_answer(request, *args, **kwargs) -> 'JsonResponse':
    """https://docs.djangoproject.com/en/2.2/topics/http/sessions/#when-sessions-are-saved
    """
    problem_id = kwargs['problem_id']
    form = WorksheetProblemForm(request.POST)
    json = {
        'result': 'invalid form'
    }
    if form.is_valid():
        user_answer = form.cleaned_data['user_answer']
        problem = Problem.objects.filter(id=problem_id).first()
        correct_answer = problem.calculated_answer
        checked_problems = request.session.setdefault('checked_problems', dict(right=list(), wrong=list()))
        if user_answer == correct_answer or sn_round(user_answer) == sn_round(correct_answer):
            if problem_id not in checked_problems['right']:
                checked_problems['right'].append(problem_id)
            if problem_id in checked_problems['wrong']:
                checked_problems['wrong'].remove(problem_id)
            json['result'] = 'right'
        else:
            if problem_id not in checked_problems['wrong']:
                checked_problems['wrong'].append(problem_id)
            if problem_id in checked_problems['right']:
                checked_problems['right'].remove(problem_id)
            json['result'] = 'wrong'
        request.session.modified = True
    return JsonResponse(json)


def worksheets_reset(request, *args, **kwargs):
    checked_problems = request.session.get('checked_problems')
    if checked_problems:
        # Get course and worksheet info
        course = course_from_kwargs(kwargs)
        worksheet = Worksheet.objects.filter(
            course=course,
            title=kwargs['worksheet_title'],
        ).first()
        # Clear worksheet problems from checked_problems
        worksheet_problem_ids = ( str(problem.id) for problem in worksheet.problem_set.all() )
        for value in checked_problems.values():
            for problem_id in worksheet_problem_ids:
                if problem_id in value:
                    value.remove(problem_id)
        # Tell django we updated the session
        request.session.modified = True
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_reset_all(request, *args, **kwargs):
    if request.session.get('checked_problems'):
        del request.session['checked_problems']
    return redirect('course-worksheets', *args, **kwargs)
# END worksheet view functions ------------------------------------------------>


def resources(request, *args, **kwargs):
    course = course = course_from_kwargs(kwargs)
    context = {
        'course': course,
        'resources': course.resources,
    }
    return render(request, 'courses/course_resources.html', context)
