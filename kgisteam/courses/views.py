from django.shortcuts import redirect, render

from courses.models import Course

def courses_home(request):
    context = {
        'courses': Course.objects.all(),
    }
    return render(request, 'courses/courses_home.html', context)
