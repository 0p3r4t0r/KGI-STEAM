import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from courses.models import Course, Problem
from courses.validators import validate_math_expression
from courses.maths import evaluate_answer, sn_round


class CourseAdminForm(forms.ModelForm):
    class Meta:
        exclude = ('nen_kumi',)
        model = Course

    def clean_term1_start(self):
        """Make sure term1 starts in the same year as course.year"""
        date1 = self.cleaned_data.get('term1_start')
        if date1:
            if date1.year != self.cleaned_data['year']:
                raise ValidationError(
                    'First term should start in the same year as the course.',
                    code='invalid',
                )
        return self.cleaned_data['term1_start']

    def clean_term2_start(self):
        date1 = self.cleaned_data.get('term1_start')
        date2 = self.cleaned_data.get('term2_start')
        if date1 and date2:
            if date2 <= date1:
                raise ValidationError(
                    'Second term should start after first term!',
                    code='invalid',
                )
        return self.cleaned_data['term2_start']

    def clean_term3_start(self):
        """Make sure term1 starts in the same year as course.year"""
        date2 = self.cleaned_data.get('term2_start')
        date3 = self.cleaned_data.get('term3_start')
        if date2 and date3:
            if date3 <= date2:
                raise ValidationError(
                    'Third term should start after second term!',
                    code='invalid',
                )
        return self.cleaned_data['term3_start']

    def clean_term4_start(self):
        """Make sure term1 starts in the same year as course.year"""
        date3 = self.cleaned_data.get('term3_start')
        date4 = self.cleaned_data.get('term4_start')
        if date3 and date4:
            if date4 <= date3:
                raise ValidationError(
                    'Fourth term should start after third term!',
                    code='invalid',
                )
        return self.cleaned_data['term4_start']

class ProblemInlineForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Problem

    def clean_answer(self):
        vars_with_vals = self.cleaned_data['variables_with_values']
        answer = self.cleaned_data['answer']
        # Check to make sure all vars begin with '$'
        words_in_answer = re.findall(r'\b(?<!\$)[^0-9\.*+-\/\s]+\b', answer)
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
        if not vars.issuperset(answer_vars):
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
