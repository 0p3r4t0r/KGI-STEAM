from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from courses.models import Course


def courses_home(request):
    context = {
        'courses': Course.objects.all(),
    }
    return render(request, 'courses/courses_home.html', context)


class CourseView(TemplateView):
    template = 'courses/course.html'
