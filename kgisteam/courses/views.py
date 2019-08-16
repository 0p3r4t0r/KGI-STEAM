from collections import OrderedDict

from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from courses.forms import WorksheetForm
from courses.models import Course, Problem, Resource, Syllabus, Worksheet


def courses_home(request):
    context = {
        'courses': Course.objects.all(),
    }
    return render(request, 'courses/courses_home.html', context)


class CourseView(TemplateView):
    template_name = 'courses/course_base.html'
    template404 = 'kgisteam/error_404.html'

    def answered_questions(self, is_correct=1):
        worksheet = self.get_worksheet()
        if worksheet:
            session = self.request.session
            problems = worksheet.problem_set.all()
            correctly_answered = set()
            for problem in problems:
                problem_key = 'problem{}'.format(problem.id)
                if problem_key in session.keys():
                    if session[problem_key] == is_correct:
                        correctly_answered.add(problem.id)
            return correctly_answered

    def get(self, request, *args, **kwargs):
        if self.get_course():
            return render(request, self.template_name, self.get_context_data())
        else:
            return render(request, self.template404)

    def get_course(self):
        course = Course.objects.filter(
            school=self.kwargs['school'],
            name=self.kwargs['name'],
            nen=self.kwargs['nen_kumi'][0],
            kumi=self.kwargs['nen_kumi'][2],
            year=self.kwargs['year'],
        ).first()
        return course

    def get_problems(self, order_by=None):
        worksheet = self.get_worksheet()
        if worksheet:
            if self.kwargs['order'] == 'random':
                problems = worksheet.problem_set.order_by('?')
                return problems
            else:
                problems = worksheet.problem_set.all()
                return problems

    def get_resources(self, category):
        course = self.get_course()
        resources = set(Resource.objects.filter(category=category))
        return resources

    def get_syllabus(self):
        # Find the course syllabus data.
        syllabus = Syllabus.objects.filter(
            course=self.get_course(),
        ).first()
        return syllabus

    def get_worksheet(self):
        worksheet_set = self.get_worksheet_set()
        if 'worksheet_title' in self.kwargs.keys():
            worksheet = worksheet_set.filter(
                title=self.kwargs['worksheet_title']
            ).first()
            return worksheet

    def get_worksheet_set(self):
        course = self.get_course()
        worksheet_set = course.worksheet_set.all()
        return worksheet_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.get_course()
        # Syllabus and lessons.
        syllabus = self.get_syllabus()
        if syllabus:
            context['lesson_set'] = syllabus.lesson_set.all()
        # Worksheets
        context['worksheet_set'] = self.get_worksheet_set()
        context['worksheet'] = self.get_worksheet()
        context['worksheet_form'] = WorksheetForm()
        context['problems'] = self.get_problems()
        context['correctly_answered'] = self.answered_questions(1)
        context['incorrectly_answered'] = self.answered_questions(0)
        # Resources
        context['resources_IC'] = self.get_resources('IC')
        context['resources_LL'] = self.get_resources('LL')
        context['resources_FS'] = self.get_resources('FS')
        context['category_resources'] = OrderedDict(
            ((category, self.get_resources(abbr))
            for (abbr, category) in Resource.CATEGORY_CHOICES)
        )
        return context


def worksheets_check_answer(request, *args, **kwargs):
    if request.method == 'POST':
        user_answer = float(request.POST['answer'])
        problem_id = kwargs.pop('problem_id')
        problem = Problem.objects.filter(
            id=problem_id,
        ).first()
        correct_answer = problem.answer
        if user_answer == correct_answer:
            request.session['problem{}'.format(problem_id)] = 1
        else:
            request.session['problem{}'.format(problem_id)] = 0
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_reset(request, *args, **kwargs):
    course = Course.objects.filter(
        school=kwargs['school'],
        name=kwargs['name'],
        nen=kwargs['nen_kumi'][0],
        kumi=kwargs['nen_kumi'][2],
        year=kwargs['year'],
    ).first()
    worksheet = Worksheet.objects.filter(
        course=course,
        title=kwargs['worksheet_title'],
    ).first()
    worksheet_problem_keys = [ 'problem{}'.format(problem.id) for problem in worksheet.problem_set.all() ]
    delete = [ key for key in request.session.keys()
                if key.startswith('problem') and
                key in worksheet_problem_keys
    ]
    for key in delete: del request.session[key]
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_reset_all(request, *args, **kwargs):
    delete = [ key for key in request.session.keys()
                if key.startswith('problem')
    ]
    for key in delete: del request.session[key]
    return redirect('course-worksheets', *args, **kwargs)


def worksheets_problems_order(request, *args, **kwargs):
    if kwargs['order'] == 'random':
        kwargs['order'] = 'ordered'
        return redirect('course-worksheets', *args, **kwargs)
    else:
        kwargs['order'] = 'random'
        return redirect('course-worksheets', *args, **kwargs)
