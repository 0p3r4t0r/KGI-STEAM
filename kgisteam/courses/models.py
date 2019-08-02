from django.core.validators import RegexValidator
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

    SCHOOL_CHOICES = [
        (MIDDLESCHOOL, 'Middle School'),
        (HIGHSCHOOL, 'High School'),
    ]
    GRADE_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
    ]


    name = models.CharField(
        max_length=30
        )
    school = models.CharField(
        max_length=2,
        choices=SCHOOL_CHOICES,
        )
    grade = models.IntegerField(
        choices=GRADE_CHOICES,
        )
    letter_number = models.CharField(
        max_length=1,
        validators=[
            # Match A-E (Middle School) or 1-8 (High School)
            RegexValidator(
                message='Middle School classes: A-E or High School classes: 1-8',
                regex='[A-E]|[1-8]',
            )
        ],
        verbose_name='Class Letter/Number',
        )
    description = models.TextField(
            blank=True,
            max_length=200,
        )
    image_source_url = models.CharField(
        blank=True,
        max_length=200,
        )
    image_path = models.ImageField(
        blank=True,
        upload_to='courses',
        )
    
