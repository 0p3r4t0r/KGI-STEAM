from django.shortcuts import redirect, render
from django.urls import reverse


def home(request):
    """The home page."""
    context = {}
    return render(request, 'home/base.html', context)


def home_redirect(request):
    """Redirects to the home page."""
    context = {}
    return redirect(request, reverse('home'), context)
