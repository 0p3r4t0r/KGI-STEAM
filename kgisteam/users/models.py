from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Substitute an extensible user model.
    
    Django recommends setting up a custom user model.
    https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#substituting-a-custom-user-model

    Django docs page for the default user model.
    https://docs.djangoproject.com/en/2.2/ref/contrib/auth/#django.contrib.auth.models.User

    AbstractUser source code.
    https://github.com/django/django/blob/master/django/contrib/auth/models.py
    """

    def __str__(self):
        return self.username

