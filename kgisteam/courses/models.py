import random

from markdown import markdown
from martor.models import MartorField
from string import Template
from taggit.managers import TaggableManager

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.urls import reverse

from courses.maths import evaluate_answer, sn_round, sn_round_str


class BaseModel(models.Model):
    class Meta:
        abstract = True

    last_modified = models.DateTimeField(auto_now=True)


class Course(BaseModel):
    MIDDLESCHOOL = 'MS'
    HIGHSCHOOL = 'HS'

    SCHOOL_CHOICES = (
        (MIDDLESCHOOL, 'Middle School'),
        (HIGHSCHOOL, 'High School'),
    )

    NEN_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
    )

    MS_KUMI_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    )

    HS_KUMI_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    )

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
    )
    description = models.TextField(
        blank=True,
        max_length=200,
    )
    image_source_url = models.URLField(
        blank=True,
        max_length=200,
    )
    image_path = models.ImageField(
        blank=True,
        upload_to='courses',
    )

    @property
    def resources(self):
        return {
            category[1]: self.resource_set.filter(category=category[0])
            for category in ResourceBaseClass.CATEGORY_CHOICES
        }

    def save(self, *args, **kwargs):
        updated_nen_kumi = '{}-{}'.format(self.nen, self.kumi)
        if self.nen_kumi != updated_nen_kumi:
            self.nen_kumi = updated_nen_kumi
        super().save(*args, **kwargs)

    def __str__(self):
        return '{name} ({school}: {nen_kumi}) {year}'.format(
            name=self.name,
            school=self.school,
            nen_kumi=self.nen_kumi,
            year=self.year,
        )


class Syllabus(BaseModel):

    class Meta:
        verbose_name_plural = "Syllabi"

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

    def get_absolute_url(self):
        kwargs={
            'year': self.course.year,
            'school': self.course.school,
            'name': self.course.name,
            'nen_kumi': self.course.nen_kumi,
        }
        return reverse('course-syllabi', kwargs=kwargs)

    def __str__(self):
        return '{} syllabus'.format(self.course)


class Lesson(BaseModel):
    url_max_length=200
    url_text_max_length=50

    def default_lesson_date():
        return timezone.now().date()

    syllabus = models.ForeignKey(
        Syllabus,
        null=True,
        on_delete=models.SET_NULL,
    )
    number = models.IntegerField(
        null=True,
    )
    date = models.DateField(
        default=default_lesson_date
    )
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

    @property
    def links(self) -> list:
        links_dict = { key: value for key, value in self.__dict__.items()
            if value and key.startswith('link')
        }
        return [
            (links_dict['link{}_URL'.format(i)], links_dict['link{}_text'.format(i)])
            for i in range(0, int(len(links_dict)/2))
        ]

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
        return timezone.make_aware(timezone.datetime.today().replace(
            hour=20, minute=0,
            second=0, microsecond=0,
            )
        )

    course = models.ManyToManyField(Course, blank=True)
    title = models.CharField(
        default=timezone.now,
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
        if self.solution_release_datetime < timezone.make_aware(timezone.datetime.now()):
            return  True
        else:
            return False


class Problem(BaseModel):
    use_vars = None

    worksheet = models.ForeignKey(
        Worksheet,
        null=True,
        on_delete=models.CASCADE,
    )
    question = MartorField(
        default='Your question here.',
        max_length=500,
    )

    # variable_name[default_value, min, max, is_int]
    variables_with_values = models.CharField(
        blank = True,
        max_length=100,
        validators=[
            RegexValidator(
                message=(
                    'Variables format is variable_name[default_value: '
                    'float, min: float, max: float, is_int: bool].'
                ),
                regex=r'([a-z|A-Z]\w*\[([0-9]+(\.?[0-9]*e?[0-9]{0,3})(,\s)?){0,3}([0-1]\])(,\s)?)*',
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

    @property
    def html_id(self):
        return 'problem-pk{}'.format(self.pk)

    @property
    def variables_as_lists(self) -> dict:
        """Return a dict of the form { variable_name: [values]"""
        if self.variables_with_values:
            variables = dict()
            for _ in [ var.strip() for var in self.variables_with_values.split('],') ]:
                # Trim the brackets
                variable_name, variable_values = _.split('[')
                variable_values = variable_values.replace(']', '')
                # Convert the numbers into a list.
                variables[variable_name] = [ float(value) for value in variable_values.split(', ') ]
            return variables
        else:
            return dict()

    @property
    def variables_as_floats(self) -> dict:
        if self.use_vars:
            return self.use_vars
        elif self.variables_with_values:
            return { key: sn_round(value[0])
                for key, value
                in self.variables_as_lists.items()
            }
        else:
            return dict()

    @property
    def variables_as_strings(self) -> dict:
        if self.use_vars:
            return { key: sn_round_str(value)
                for key, value
                in self.use_vars.items()
            }
        elif self.variables_with_values:
            return { key: sn_round_str(value)
                for key, value
                in self.variables_as_floats.items()
            }
        else:
            return dict()

    @property
    def is_randomizable(self) -> bool:
        is_randomizable = False
        if self.variables_as_lists:
            for name, value in self.variables_as_lists.items():
                len_value = len(value)
                if len_value == 4 or len_value == 3:
                    if value[1] != value[2]:
                        is_randomizable = True
                if len_value == 2:
                    if value[0] != value[1]:
                        is_randomizable = True
                if len_value == 1:
                    is_randomizable = False
        return is_randomizable

    def variables_randomized(self) -> dict:
        vars = dict()
        if self.variables_as_lists:
            for name, value in self.variables_as_lists.items():
                len_value = len(value)
                if len_value == 4:
                    if value[3]:
                        vars[name] = int(sn_round(random.uniform(value[1], value[2])))
                    else:
                        vars[name] = sn_round(random.uniform(value[1], value[2]))
                elif len_value == 3:
                    vars[name] = sn_round(random.uniform(value[1], value[2]))
                elif len_value == 2:
                    vars[name] = sn_round(random.uniform(value[0], value[1]))
                else:
                    vars[name] = sn_round(value[0])
            return vars

    def use_variables(self, use_vars: dict) -> None:
        self.use_vars = use_vars

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
                release_datetime_local = timezone.localtime(self.worksheet.solution_release_datetime)
                release_date_str = release_datetime_local.strftime('%y-%m-%d')
                release_time_str = release_datetime_local.strftime('%H:%M')
                return markdown(
                    'Solutions will be released on {release_date}, at {release_time}.'.format(
                        release_date=release_date_str,
                        release_time=release_time_str,
                    )
                )

    def calculate_answer(self):
        if self.use_vars:
            answer_template = Template(self.answer)
            answer = evaluate_answer(
                answer_template.safe_substitute(**self.use_vars)
            )
        elif self.variables_with_values:
            answer_template = Template(self.answer)
            answer = evaluate_answer(
                answer_template.safe_substitute(**self.variables_as_floats)
            )
        else:
            answer = evaluate_answer(self.answer)
        answer_rounded = sn_round(answer)
        return answer_rounded

    def check_user_answer(self, user_answer):
        if sn_round(user_answer) == self.calculated_answer:
            return True
        elif sn_round(user_answer) == self.calculate_answer():
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        """ Save the calculated_answer
        https://docs.djangoproject.com/en/2.2/topics/db/models/#overriding-predefined-model-methods"""
        self.calculated_answer = self.calculate_answer()
        super().save(*args, **kwargs)  # Call the "real" save() method.


class ResourceBaseClass(models.Model):
    class Meta:
        abstract=True

    IN_CLASS = 'IC'
    LANGUAGE_LEARNING = 'LL'
    FURTHER_STUDY = 'FS'

    CATEGORY_CHOICES = [
        (IN_CLASS, 'In Class'),
        (LANGUAGE_LEARNING, 'Language Learning'),
        (FURTHER_STUDY, 'Further Study'),
    ]

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
