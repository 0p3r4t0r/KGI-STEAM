from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserChangeForm(UserChangeForm):
    """Change an existing CustomUser."""
    pass


class CustomUserCreationForm(UserCreationForm):
    """Create an instance of CustomUser."""
    pass
