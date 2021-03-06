# Generated by Django 3.0.2 on 2020-02-05 00:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0023_problem_variables_with_values_validator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='variables_with_values',
            field=models.CharField(blank=True, max_length=100, validators=[django.core.validators.RegexValidator(message='Variables format is variable_name[default_value: float, min: float, max: float, is_int: bool].', regex='([a-z|A-Z]\\w*\\[([0-9]+(\\.?[0-9]*e?[0-9]{0,3})(,\\s)?){0,3}([0-1]\\])(,\\s)?)*')]),
        ),
    ]
