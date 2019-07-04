from django.db import models

"""

"""


class Course(models.Model):
    """Store course information.
    
    course_name --> You should be careful about support for Japanese.
    course_school --> Middle School or High School (MS or HS)
    course_grade --> MS and HS: 1-3
    course_class --> MS: A-E and HS: 1-8


    course_image --> an optional field to add and image for your course.
    
    course_syllabus --> relation? separate app?
    course_worksheets --> relation? separate app?
    """
    MIDDLESCHOOL = 'MS'
    HIGHSCHOOL = 'HS'    

    GRADE_CHOICES = [
        (MIDDLESCHOOL, 'Middle School'),
        (HIGHSCHOOL, 'High School'),
    ]


    course_name = models.CharField(
        max_length=30
        )
    course_school = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        )
    course_grade = models.IntegerField(
        max_length=1,
        # validator that only allows 1-3.
        )
    course_class = models.CharField(
        max_length=1,
        # validator that only allows A-E or 1-8
        )
