from django.shortcuts import redirect, render
from django.urls import reverse


def home(request):
    """The home page."""
    context = {
        'steam_acronym': ('Science', 'Technology', 'Engineering', 
                            'Art', 'Mathematics',)
    }
    return render(request, 'home/home.html', context)


def home_redirect(request):
    """Redirects to the home page."""
    context = {}
    return redirect(request, reverse('home'), context)
