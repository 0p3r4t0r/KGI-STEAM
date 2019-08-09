from django import forms
from django.core.validators import DecimalValidator

from courses.models import Problem
from courses.models import Problem


class WorksheetForm(forms.Form):
    problem_answer_field = Problem._meta.get_field('answer')
    answer = forms.FloatField(
        label='your answer',
    )
