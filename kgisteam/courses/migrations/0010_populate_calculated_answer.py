# Generated by Django 2.2.5 on 2019-09-26 03:01
# https://docs.djangoproject.com/en/2.2/topics/migrations/#data-migrations

from django.db import migrations

from courses.models import Problem


def populate_calculated_answer(apps, schema_editor):
    for problem in Problem.objects.all():
        problem.calculated_answer = problem.calculate_answer()
        problem.save()

def unpopulate_calculated_answer(apps, schema_editor):
    for problem in Problem.objects.all():
        problem.calculated_answer = None
        problem.save()


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_problem_calculated_answer'),
    ]

    operations = [
        migrations.RunPython(populate_calculated_answer, unpopulate_calculated_answer),
    ]
