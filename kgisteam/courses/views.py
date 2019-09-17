from collections import OrderedDict
from copy import deepcopy
from math import trunc

from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from courses.forms import WorksheetProblemForm
from courses.models import CATEGORY_CHOICES
from courses.models import Course, CourseResource, Problem, SharedResource, Syllabus, Worksheet
from courses.utils import sn_round


def courses_home(request):
    context = {
        'courses': Course.objects.order_by('-school', 'nen', 'kumi'),
    }
    return render(request, 'courses/courses_home.html', context)


class CourseView(TemplateView):

    template_name = 'courses/course_base.html'

    @property
    def active_problems(self):
        if 'order' in self.kwargs.keys() and self.active_worksheet:
            if self.kwargs['order'] == 'random':
                return self.active_worksheet.problem_set.order_by('?')
            else:
                return self.active_worksheet.problem_set.all()

    @property
    def active_worksheet(self):
        if 'worksheet_title' in self.kwargs.keys():
            worksheet = self.course.worksheet_set.filter(
                title=self.kwargs['worksheet_title']
            ).first()
            return worksheet

    def answered_questions(self, is_correct=1):
        if self.active_worksheet:
            session = self.request.session
            problems = self.active_worksheet.problem_set.all()
            correctly_answered = set()
            for problem in problems:
                problem_key = 'problem{}'.format(problem.id)
                if problem_key in session.keys():
                    if session[problem_key] == is_correct:
                        correctly_answered.add(problem.id)
            return correctly_answered

    def get(self, request, *args, **kwargs):
        if self.course:
            return render(request, self.template_name, self.get_context_data())
        else:
            return render(request, self.template404)

    @property
    def course(self):
        course = Course.objects.filter(
            school=self.kwargs['school'],
            name=self.kwargs['name'],
            nen=self.kwargs['nen_kumi'][0],
            kumi=self.kwargs['nen_kumi'][2],
            year=self.kwargs['year'],
        ).first()
        return course

    @property
    def resources(self):
        category_choices = CATEGORY_CHOICES
        shared_resources = SharedResource.objects.all()
        course_resources = CourseResource.objects.filter(course=self.course)
        resources = dict()
        for category in category_choices:
            resources[category[1]] = (
                list(shared_resources.filter(category=category[0])) +
                list(course_resources.filter(category=category[0]))
            )
        return resources

    @property
    def syllabus(self):
        # Find the course syllabus data.
        syllabus = Syllabus.objects.filter(
            course=self.course,
        ).first()
        return syllabus

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['syllabus'] = self.syllabus
        context['active_worksheet'] = self.active_worksheet
        context['active_problems'] = self.active_problems
        context['worksheet_problem_form'] = WorksheetProblemForm()
        context['correctly_answered'] = self.answered_questions(1)
        context['incorrectly_answered'] = self.answered_questions(0)
        # Resources
        context['resources'] = self.resources
        return context


# Roughly refactored
def course_from_kwargs(kwargs):
    """make this a decorator"""
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


def resources(request, *args, **kwargs):
    course = course = course_from_kwargs(kwargs)
    context = {
        'course': course,
        'resources': course.resources,
    }
    return render(request, 'courses/course_resources.html', context)


def worksheets(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    active_worksheet = course.worksheet_set.filter(
        title=kwargs['worksheet_title']
    ).first()
    context = {
        'course': course,
    }
    if active_worksheet:
        active_problems = active_worksheet.problem_set.all()
        context['active_worksheet'] = active_worksheet
        context['active_problems'] = active_problems
        context['worksheet_problem_form'] = WorksheetProblemForm()
        context['problem_order'] = kwargs['order']
        if 'checked_problems' in request.session.keys():
            context['checked_problems'] = request.session['checked_problems']
    return render(request, 'courses/course_worksheets.html', context)


def worksheets_check_answer(request, *args, **kwargs):
    """https://docs.djangoproject.com/en/2.2/topics/http/sessions/#when-sessions-are-saved
    """
    problem_id = kwargs.pop('problem_id')
    if request.method == 'POST':
        form = WorksheetProblemForm(request.POST)
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
            else:
                if problem_id not in checked_problems['wrong']:
                    checked_problems['wrong'].append(problem_id)
                if problem_id in checked_problems['right']:
                    checked_problems['right'].remove(problem_id)
            # Tell Django we updated the session.
            request.session.modified = True
    return redirect('course-worksheets', *args, **kwargs)

    
def worksheets_reset(request, *args, **kwargs):
    course = course_from_kwargs(kwargs)
    worksheet = Worksheet.objects.filter(
        course=course,
        title=kwargs['worksheet_title'],
    ).first()
    worksheet_problem_ids = [ str(problem.id) for problem in worksheet.problem_set.all() ]
    if 'checked_problems' in request.session.keys():
        checked_problems = request.session['checked_problems']
        for value in checked_problems.values():
            for problem_id in worksheet_problem_ids:
                if problem_id in value:
                    value.remove(problem_id)
        request.session.modified = True
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_reset_all(request, *args, **kwargs):
    if 'checked_problems' in request.session.keys():
        del request.session['checked_problems']
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_problems_order(request, *args, **kwargs):
    if kwargs['order'] == 'random':
        kwargs['order'] = 'ordered'
        return redirect('course-worksheets', *args, **kwargs)
    else:
        kwargs['order'] = 'random'
        return redirect('course-worksheets', *args, **kwargs)
