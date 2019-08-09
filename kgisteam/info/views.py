from collections import namedtuple

from django.apps import apps
from django.shortcuts import redirect, render
from django.urls import reverse


# App metadata
courses_config = apps.get_app_config('courses')


def info_home(request):
    """The info page."""
    context = {
        'app_configs': (courses_config),
        'steam_acronym': ('Keyless', 'Science', 'Technology', 'Engineering', 
                            'Art', 'Mathematics',),
    }
    return render(request, 'info/info_home.html', context)
