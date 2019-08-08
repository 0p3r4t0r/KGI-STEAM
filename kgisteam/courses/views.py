from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from courses.models import Course, Syllabus


def courses_home(request):
    context = {
        'courses': Course.objects.all(),
    }
    return render(request, 'courses/courses_home.html', context)


class CourseView(TemplateView):
    template = 'courses/course.html'
    template404 = 'kgisteam/error_404.html'

    def get(self, request, *args, **kwargs):
        if self.get_course():
            return render(request, self.template, self.get_context_data())
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

    def get_syllabus(self):
        # Find the course syllabus data.
        syllabus = Syllabus.objects.filter(
            course=self.get_course(),
        ).first()
        return syllabus

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.get_course()
        syllabus = self.get_syllabus()
        if syllabus:
            context['lesson_set'] = syllabus.lesson_set.all()
        return context
