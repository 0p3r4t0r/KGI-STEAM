import copy
import datetime
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from string import Template
from taggit.managers import TaggableManager

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

"""

"""


class Course(models.Model):
    """Store course information.

    course_name --> You should be careful about support for Japanese.
    course_school --> Middle School or High School (MS or HS)
    course_nen --> MS and HS: 1-3
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
    NEN_CHOICES = [
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
    nen = models.IntegerField(
        choices=NEN_CHOICES,
        verbose_name='nen (year)'
        )
    kumi = models.CharField(
        max_length=1,
        validators=[
            # Match A-E (Middle School) or 1-8 (High School)
            RegexValidator(
                message='Middle School classes: A-E or High School classes: 1-8',
                regex='[A-E]|[1-8]',
            )
        ],
        verbose_name='kumi (class)',
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
        return '{nen}-{kumi}'.format(
            nen=self.nen,
            kumi=self.kumi,
        )


    def __str__(self):
        return '{name} ({school}: {nen_kumi}) {year}'.format(
            name=self.name,
            school=self.school,
            nen_kumi=self.nen_kumi(),
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
    link0_URL = models.URLField(
        blank=True,
        max_length=url_max_length,
    )
    link0_text = models.CharField(
        blank=True,
        max_length=url_text_max_length,
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


    def links(self):
        links_dict = { key: value for key, value in self.__dict__.items()
            if key.startswith('link')
        }
        links = []
        # Calculate the maximum number of links a lesson can have.
        max_links_num = int(len(links_dict)/2)
        for i in range(0, max_links_num):
            url = links_dict['link{}_URL'.format(i)]
            text = links_dict['link{}_text'.format(i)]
            if url and text:
                links.append(
                    (url, text)
                )
            elif url and not text:
                links.append(
                    (url, url)
                )
        return links


class Worksheet(models.Model):
    course = models.ForeignKey(
        Course,
        null=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(
        default=datetime.datetime.now,
        max_length=50,
        unique=True,
    )
    tags = TaggableManager(
        blank=True,
    )


class Problem(models.Model):
    """
    https://neutronx.github.io/django-markdownx/
    """
    worksheet = models.ForeignKey(
        Worksheet,
        null=True,
        on_delete=models.CASCADE,
    )
    question = MarkdownxField(
        default='Your question here.',
        max_length=500,
    )
    variable_names = models.CharField(
        blank = True,
        max_length=100,
    )
    variable_default_values = models.CharField(
        blank = True,
        max_length=100,
    )
    answer = models.CharField(
        max_length=100,
    )
    solution = MarkdownxField(
        default='Your solution here.',
        max_length=1000,
    )

    @property
    def calculated_answer(self):
        if self.variables:
            return eval(self.answer.format(**self.variables))
        else:
            return float(self.answer)

    @property
    def variables(self):
        if self.variable_names and self.variable_default_values:
            variables = zip(
                self.variable_names.split(','),
                self.variable_default_values.split(',')
            )
            variables = dict(variables)
            variables = { key.strip(): float(value.strip())
                for key, value in variables.items()
            }
            return variables

    @property
    def question_markdown(self):
        """
        https://github.com/neutronX/django-markdownx/issues/74#issuecomment-340216995

        Use a template to substitute variables.
        https://docs.python.org/3/library/string.html#template-strings
        """
        if self.variables:
            template = Template(self.question)
            question = template.safe_substitute(**self.variables)
            return markdownify(question)
        else:
            return markdownify(self.question)

    @property
    def solution_markdown(self):
        """
        see the docstring for self.question_markdown
        """
        if self.variables:
            variables = copy.deepcopy(self.variables)
            variables['calculated_answer'] = self.calculated_answer
            template = Template(self.solution)
            solution = template.safe_substitute(**variables)
            return markdownify(solution)
        else:
            return markdownify(self.solution)


class Resource(models.Model):
    url_max_length=200
    url_text_max_length=30

    IN_CLASS = 'IC'
    LANGUAGE_LEARNING = 'LL'
    FURTHER_STUDY = 'FS'

    CATEGORY_CHOICES = [
        (IN_CLASS, 'In Class'),
        (LANGUAGE_LEARNING, 'Language Learning'),
        (FURTHER_STUDY, 'Further Study'),
    ]

    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        )
    link_URL = models.URLField(
        blank=True,
        max_length=url_max_length,
    )
    link_text = models.CharField(
        blank=True,
        max_length=url_text_max_length,
    )
    description = models.TextField(
        blank=True,
        max_length=200,
    )

    def __str__(self):
        return '{}: {}'.format(self.category, self.link_text)


class CourseResource(Resource):
    course = models.ForeignKey(
        Course,
        null=True,
        on_delete=models.CASCADE,
    )
