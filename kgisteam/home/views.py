from collections import namedtuple

from django.apps import apps
from django.shortcuts import redirect, render
from django.urls import reverse


# App metadata
courses_config = apps.get_app_config('courses')
worksheets_config = apps.get_app_config('worksheets')


def home(request):
    """The home page."""
    context = {
        'app_configs': (courses_config, worksheets_config,),
        'steam_acronym': ('Keyless', 'Science', 'Technology', 'Engineering', 
                            'Art', 'Mathematics',),
    }
    return render(request, 'home/home.html', context)


def home_redirect(request):
    """Redirects to the home page."""
    context = {}
    return redirect(request, reverse('home'), context)
