import datetime

from django.core.validators import MinValueValidator, RegexValidator
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

    year = models.IntegerField(
        default=2019,
        validators=[
            MinValueValidator(
                2019,
                message='No courses before 2019.',
            ),
        ]
    )
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


    def nen_kumi(self):
        return '{grade}-{letter_number}'.format(
            grade=self.grade,
            letter_number=self.letter_number,
        )


    def __str__(self):
        return '{name} ({school}: {grade}-{letter_number}) {year}'.format(
            name=self.name,
            school=self.school,
            grade=self.grade,
            letter_number=self.letter_number,
            year=self.year,
        )


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
    url_max_length=200
    url_text_max_length=30

    syllabus = models.ForeignKey(
        Syllabus,
        null=True,
        on_delete=models.SET_NULL,
    )
    number = models.IntegerField(
        null=True,
    )
    date = models.DateField()
    quiz = models.CharField(
        blank=True,
        max_length=30,
    )
    topics = models.CharField(
        blank=True,
        max_length=60,
    )
    reading = models.CharField(
        blank=True,
        max_length=60,
    )
    homework = models.CharField(
        blank=True,
        max_length=60,
    )
    link1_URL = models.URLField(
        blank=True,
        max_length=url_max_length,
    )
    link1_text = models.CharField(
        blank=True,
        max_length=url_text_max_length,
    )
    link2_URL = models.URLField(
        blank=True,
        max_length=url_max_length,
    )
    link2_text = models.CharField(
        blank=True,
        max_length=url_text_max_length,
    )
    link3_URL = models.URLField(
        blank=True,
        max_length=url_max_length,
    )
    link3_text = models.CharField(
        blank=True,
        max_length=url_text_max_length,
    )
    link4_URL = models.URLField(
        blank=True,
        max_length=url_max_length,
    )
    link4_text = models.CharField(
        blank=True,
        max_length=url_text_max_length,
    )
