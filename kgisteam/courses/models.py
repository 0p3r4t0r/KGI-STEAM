import copy
import datetime

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from string import Template
from taggit.managers import TaggableManager

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import localtime, make_aware
from django.urls import reverse

from courses.maths import evaluate_answer, sn_round, sn_round_str
from kgisteam.settings import TIME_ZONE


class BaseModel(models.Model):
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


IN_CLASS = 'IC'
LANGUAGE_LEARNING = 'LL'
FURTHER_STUDY = 'FS'

CATEGORY_CHOICES = [
    (IN_CLASS, 'In Class'),
    (LANGUAGE_LEARNING, 'Language Learning'),
    (FURTHER_STUDY, 'Further Study'),
]


class Course(BaseModel):
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

    @property
    def nen_kumi(self):
        return '{nen}-{kumi}'.format(
            nen=self.nen,
            kumi=self.kumi,
        )

    @property
    def resources(self):
        shared_resources = self.resource_set.all()
        resources = dict()
        for category in CATEGORY_CHOICES:
            resources[category[1]] = (
                list(shared_resources.filter(category=category[0]))
            )
        return resources

    def __str__(self):
        return '{name} ({school}: {nen_kumi}) {year}'.format(
            name=self.name,
            school=self.school,
            nen_kumi=self.nen_kumi,
            year=self.year,
        )


class Syllabus(BaseModel):
    # Dates can be compared the the tuples below.
    # (month, day)
    start_t1    = (4, 1)
    end_t1      = (7, 19)
    start_t2    = (9, 2)
    end_t2      = (12, 21)
    start_t3    = (1, 8)
    end_t3      = (3, 23)

    course = models.OneToOneField(
        Course,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name_plural = "Syllabi"

    def __str__(self):
        return '{} syllabus'.format(self.course)

    def get_absolute_url(self):
        kwargs={
            'year': self.course.year,
            'school': self.course.school,
            'name': self.course.name,
            'nen_kumi': str(self.course.nen) + '-' + str(self.course.kumi),
        }
        return reverse('course-syllabi', kwargs=kwargs)


class Lesson(BaseModel):
    url_max_length=200
    url_text_max_length=50

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

    @property
    def trimester(self):
        if self.syllabus.start_t1 <= (self.date.month, self.date.day) <= self.syllabus.end_t1:
            return 1
        elif self.syllabus.start_t2 <= (self.date.month, self.date.day) <= self.syllabus.end_t2:
            return 2
        elif self.syllabus.start_t3 <= (self.date.month, self.date.day) <= self.syllabus.end_t3:
            return 3


class Worksheet(BaseModel):

    def default_release_date():
        return make_aware(datetime.datetime.today().replace(
            hour=20, minute=0,
            second=0, microsecond=0,
            )
        )

    course = models.ManyToManyField(Course)
    title = models.CharField(
        default=datetime.datetime.now,
        max_length=50,
        unique=True,
    )
    tags = TaggableManager(
        blank=True,
    )
    solution_release_datetime = models.DateTimeField(
        default=default_release_date
        )


    @property
    def solutions_released(self):
        ''' Determine if solutions should be displayed whilst taking timezones
        into account.
        '''
        if self.solution_release_datetime < make_aware(datetime.datetime.now()):
            return  True
        else:
            return False


class Problem(BaseModel):
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
    calculated_answer = models.FloatField(
        blank=True,
        max_length=100,
        null=True,
    )
    answer_units = models.CharField(
        blank=True,
        max_length=50,
    )
    solution = MarkdownxField(
        default='The solution to this problem is not available yet.',
        max_length=1000,
    )

    def save(self, *args, **kwargs):
        """ Save the calculated_answer
        https://docs.djangoproject.com/en/2.2/topics/db/models/#overriding-predefined-model-methods"""
        self.calculated_answer = self.calculate_answer()
        super().save(*args, **kwargs)  # Call the "real" save() method.
        #do_something_else()

    def calculate_answer(self):
        if self.variables:
            template = Template(self.answer)
            answer = evaluate_answer(template.safe_substitute(**self.variables))
        else:
            answer = evaluate_answer(self.answer)
        answer_rounded = sn_round(answer)
        return answer_rounded

    @property
    def html_id(self):
        return 'problem-pk{}'.format(self.pk)

    @property
    def variables(self):
        if self.variable_names and self.variable_default_values:
            variables = zip(
                self.variable_names.split(','),
                self.variable_default_values.split(',')
            )
            variables = dict(variables)
            variables = { key.strip(): sn_round(float(value.strip()))
                for key, value in variables.items()
            }
            return variables

    def check_user_answer(self, user_answer):
        if user_answer == self.calculated_answer or sn_round(user_answer) == self.calculated_answer:
            return True
        else:
            return False

    @property
    def question_markdown(self):
        """
        https://github.com/neutronX/django-markdownx/issues/74#issuecomment-340216995

        Use a template to substitute variables.
        https://docs.python.org/3/library/string.html#template-strings
        """
        if self.variables:
            template = Template(self.question)
            variables = { key: sn_round_str(value)
                for key, value
                in self.variables.items()
            }
            question = template.safe_substitute(**variables)
            return markdownify(question)
        else:
            return markdownify(self.question)

    @property
    def solution_markdown(self):
        """
        see the docstring for self.question_markdown
        """
        if self.worksheet.solutions_released:
            if self.variables:
                variables = copy.deepcopy(self.variables)
                variables['calculated_answer'] = self.calculated_answer
                template = Template(self.solution)
                solution = template.safe_substitute(**variables)
                return markdownify(solution)
            else:
                return markdownify(self.solution)
        else:
                release_datetime_local = localtime(self.worksheet.solution_release_datetime)
                release_date_str = release_datetime_local.strftime('%y-%m-%d')
                release_time_str = release_datetime_local.strftime('%H:%M')
                return markdownify(
                    'Solutions will be released on {release_date}, at {release_time}.'.format(
                        release_date=release_date_str,
                        release_time=release_time_str,
                    )
                )


class ResourceBaseClass(models.Model):

    class Meta:
        abstract=True

    url_max_length=200
    url_text_max_length=30

    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_CHOICES[0],
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


class Resource(ResourceBaseClass):
    courses = models.ManyToManyField(Course, blank=True)
