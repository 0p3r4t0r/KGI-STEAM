import re

from django import forms
from django.core.exceptions import ValidationError

from courses.models import Problem
from courses.validators import validate_math_expression
from courses.maths import evaluate_answer, sn_round


class ProblemInlineForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Problem

    def clean_answer(self):
        vars_with_vals = self.cleaned_data['variables_with_values']
        answer = self.cleaned_data['answer']
        # Check to make sure all vars begin with '$'
        words_in_answer = re.findall(r'\b(?<!\$)\w+\b', answer)
        if words_in_answer:
            raise ValidationError(
                "Variables names must begin with '$'",
                code='invalid',
            )
        # Check that all variables are defined.
        vars = set(re.findall(r'\w+(?=\[)', vars_with_vals))
        answer_vars = set( 
            re.findall(r'(?<=\$)\w+', answer) +     # names without brackets 
            re.findall(r'(?<=\$){([^}]+)}', answer) # names with brackets
        )
        if vars != answer_vars:
            raise ValidationError(
                'Undefined variable(s): %(value)s',
                code='invalid',
                params={'value': sorted(answer_vars)},
            )
        return self.cleaned_data['answer']


class WorksheetProblemForm(forms.Form):
    user_answer = forms.CharField(
        label='',
        validators=[validate_math_expression],
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            }
        )
    )

    def clean_user_answer(self) -> float:
        """https://docs.djangoproject.com/en/2.2/ref/forms/validation/"""
        user_answer = evaluate_answer(self.cleaned_data['user_answer'])
        user_answer_rounded = sn_round(user_answer)
        return user_answer_rounded
