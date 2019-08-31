from collections import namedtuple

from django.apps import apps
from django.shortcuts import redirect, render
from django.urls import reverse


def info_home(request):
    """The info page."""
    context = {
        'steam_acronym': ('Keyless', 'Grading', 'Interface',
            'Science', 'Technology', 'Engineering', 'Art', 'Mathematics',),
    }
    return render(request, 'info/info_home.html', context)
