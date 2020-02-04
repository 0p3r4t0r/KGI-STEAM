import datetime
import random

from markdown import markdown
from martor.models import MartorField
from string import Template
from taggit.managers import TaggableManager

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import localtime, make_aware
from django.urls import reverse

from courses.maths import evaluate_answer, sn_round, sn_round_str


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
            RegexValidator(
                message='Middle School classes: A-E or High School classes: 1-8',
                regex='[A-E]|[1-8]',
            )
        ],
        verbose_name='kumi (class)',
        )
    nen_kumi = models.CharField(
            blank=True,
            max_length=3,
            validators=[
                RegexValidator(
                    message='Middle School classes: A-E or High School classes: 1-8',
                    regex='[1-3]-([A-E]|[1-8])',
                )
            ],
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
    def resources(self):
        shared_resources = self.resource_set.all()
        resources = dict()
        for category in CATEGORY_CHOICES:
            resources[category[1]] = (
                list(shared_resources.filter(category=category[0]))
            )
        return resources

    def save(self, *args, **kwargs):
        updated_nen_kumi = '{}-{}'.format(self.nen, self.kumi)
        if self.nen_kumi != updated_nen_kumi:
            self.nen_kumi = updated_nen_kumi 
        super().save(*args, **kwargs)  # Call the "real" save() method.

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
    description = models.TextField(
        blank=True,
        max_length=300,
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
    randomized_vars = None
    
    worksheet = models.ForeignKey(
        Worksheet,
        null=True,
        on_delete=models.CASCADE,
    )
    question = MartorField(
        default='Your question here.',
        max_length=500,
    )
    # variable_name[default_value, min, max, step]
    variables_with_values = models.CharField(
        blank = True,
        max_length=100,
        validators=[
            RegexValidator(
                message='Variables format is variable_name[default_value, min, max, step].',
                regex=r'([a-z|A-Z]\w*\[([0-9]+(\.?[0-9]*e?[0-9]{0,3})(,\s)?){0,3}([0-9]+\.?[0-9]*e?[0-9]{0,3}\])(,\s)?)*',
            )
        ],
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
    solution = MartorField(
        default='The solution to this problem is not available yet.',
        max_length=1000,
    )

    def save(self, *args, **kwargs):
        """ Save the calculated_answer
        https://docs.djangoproject.com/en/2.2/topics/db/models/#overriding-predefined-model-methods"""
        self.calculated_answer = self.calculate_answer()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def calculate_answer(self):
        if self.randomized_vars:
            answer_template = Template(self.answer)
            answer = evaluate_answer(
                answer_template.safe_substitute(**self.randomized_vars)
            )
        elif self.variables_with_values:
            answer_template = Template(self.answer)
            answer = evaluate_answer(
                answer_template.safe_substitute(**self.variables_as_floats())
            )
        else:
            answer = evaluate_answer(self.answer)
        answer_rounded = sn_round(answer)
        return answer_rounded

    @property
    def html_id(self):
        return 'problem-pk{}'.format(self.pk)

    @property
    def variables(self) -> dict:
        """Return a dict of the form { variable_name: [values]"""
        if self.variables_with_values:
            variables = dict()
            for _ in [ var.strip() for var in self.variables_with_values.split('],') ]:
                # Trim the brackets
                variable_name, variable_values = _.split('[')
                variable_values = variable_values.replace(']', '')
                # Convet the numbers into a list.
                variables[variable_name] = [ float(value) for value in variable_values.split(', ') ]
            return variables

    def variables_as_floats(self, randomized_vars=None) -> dict:
        if randomized_vars:
            self.randomized_vars = randomized_vars
            return randomized_vars
        else:
            vars = { key: sn_round(value[0])
                for key, value
                in self.variables.items()
            }
            return vars

    @property
    def variables_as_strings(self) -> dict:
        if self.randomized_vars:
            vars = { key: sn_round_str(value)
                for key, value
                in self.randomized_vars.items()
            }
        else:
            vars = { key: sn_round_str(value)
                for key, value
                in self.variables_as_floats().items()
            }
        return vars

    def variables_randomized(self) -> dict:
        vars = dict()
        if self.variables:
            for name, values in self.variables.items():
                if len(values) == 3 or len(values) == 4:
                    vars[name] = sn_round(random.uniform(values[1], values[2]))
            return vars

    def check_user_answer(self, user_answer):
        if sn_round(user_answer) == self.calculated_answer:
            return True
        elif sn_round(user_answer) == self.calculate_answer():
            return True
        else:
            return False

    @property
    def question_markdown(self):
        """
        Use a template to substitute variables.
        https://docs.python.org/3/library/string.html#template-strings
        """
        if self.variables_with_values:
            question_template = Template(self.question)
            question = question_template.safe_substitute(**self.variables_as_strings)
            return markdown(question)
        else:
            return markdown(self.question)

    @property
    def solution_markdown(self):
        """
        see the docstring for self.question_markdown
        """
        if self.worksheet.solutions_released:
            if self.variables_with_values:
                variables = self.variables_as_strings
                variables['calculated_answer'] = self.calculated_answer
                solution_template = Template(self.solution)
                solution = solution_template.safe_substitute(**variables)
                return markdown(solution)
            else:
                return markdown(self.solution)
        else:
                release_datetime_local = localtime(self.worksheet.solution_release_datetime)
                release_date_str = release_datetime_local.strftime('%y-%m-%d')
                release_time_str = release_datetime_local.strftime('%H:%M')
                return markdown(
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
