from django import forms
from django.core.validators import DecimalValidator

from courses.models import Problem
from courses.models import Problem
from courses.utils import sn_round


class WorksheetForm(forms.Form):
    problem_answer_field = Problem._meta.get_field('answer')
    answer = forms.FloatField(
        label='your answer',
    )

    def clean_answer(self):
        """https://docs.djangoproject.com/en/2.2/ref/forms/validation/"""
        answer = eval(self.cleaned_data.answer)
        answer_rounded = sn_round(answer)
        return answer_rounded
