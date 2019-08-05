from django.db import models

from courses.models import Course


class Syllabus(models.Model):
    course = models.OneToOneField(
        Course,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name_plural = "Syllabi"

    def __str__(self):
        return '{} syllabus'.format(self.course)


class Lesson(models.Model):
    syllabus = models.ManyToManyField(Syllabus)
    date = models.DateField()
"""
Define another class down here to hold an individual syllabus entry.
Use a one to many.

Syllabus will essentially bundle these entries and then connect them to
their corresponding course.
"""
