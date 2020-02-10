from django.test import TestCase
from django.utils import timezone

from courses.maths import sn_round_str
from courses.models import Course, Lesson, Problem, Resource, Syllabus, Worksheet


class TestCourse(TestCase):
    def setUp(self):
        self.hs_course = Course.objects.create(
                name='Test HS Course',
                school='HS',
                nen='1',
                kumi='1',
        )
        self.ms_course = Course.objects.create(
                name='Test MS Course',
                school='MS',
                nen='1',
                kumi='A',
        )

    def test_courses_created(self):
        self.assertEqual(Course.objects.count(), 2)
    
    def test_courses_nen_kumi_field(self):
        self.assertEqual(self.hs_course.nen_kumi, '1-1')
        self.assertEqual(self.ms_course.nen_kumi, '1-A')

class TestSyllabus(TestCase):
    num_syllabi = 2
    lessons_per_syllabus = 5
    test_link_URL = 'https://github.com/0p3r4t0r'
    test_link_text = 'GitHub: 0p3r4t0r'

    def setUp(self):
        for i in range(0, self.num_syllabi):
            syllabus = Syllabus.objects.create()
            for i in range(0, self.lessons_per_syllabus):
                lesson = Lesson.objects.create(
                    syllabus=syllabus,
                    number = i,
                    quiz='Not a quiz, but a test.',
                    topics='test, testing, tested',
                    reading='Read the docs.',
                    homework='All the homework',
                    link0_URL=self.test_link_URL,
                    link0_text=self.test_link_text,
                    link1_URL=self.test_link_URL,
                    link1_text=self.test_link_text,
                )

    def test_syllabi_created(self):
        self.assertEqual(Syllabus.objects.count(), self.num_syllabi)

    def test_lessons_created(self):
        for syllabus in Syllabus.objects.all():
            self.assertEqual(syllabus.lesson_set.count(), self.lessons_per_syllabus)

    def test_lesson_links(self):
        lesson = Lesson.objects.first()
        self.assertEqual(
            lesson.links, 
            [(self.test_link_URL, self.test_link_text),
            (self.test_link_URL, self.test_link_text)]
        )

class TestResource(TestCase):
    def setUp(self):
        for category in Resource.CATEGORY_CHOICES:
            Resource.objects.create(category=category)

    def test_resources_created(self):
        self.assertEqual(Resource.objects.count(), len(Resource.CATEGORY_CHOICES))

class TestWorksheet(TestCase):
    num_ws = 2
    problems_per_ws = 5

    def setUp(self):
        for i in range(0, self.num_ws):
            worksheet = Worksheet.objects.create(
                title='Test Worksheet {}'.format(i),
            )
            for i in range(0, self.problems_per_ws):
                Problem.objects.create(
                    worksheet=worksheet,
                    answer='42',
                )

    def test_worksheets_created(self):
        self.assertEqual(Worksheet.objects.count(), self.num_ws)

    def test_problems_created(self):
        for ws in Worksheet.objects.all():
            self.assertEqual(ws.problem_set.count(), self.problems_per_ws)

    def test_solutions_released(self):
        ws = Worksheet.objects.first()
        ws.solution_release_datetime = timezone.make_aware(
            timezone.datetime.now() - timezone.timedelta(days=1)
        )
        self.assertTrue(ws.solutions_released)
        ws.solution_release_datetime = timezone.make_aware(
            timezone.datetime.now() + timezone.timedelta(days=1)
        )
        self.assertFalse(ws.solutions_released)


class TestProblem(TestCase):
    def setUp(self):
        self.problem_without_vars = Problem.objects.create(
            question='What is 1+1?',
            answer='2'
        )
        self.problem_with_vars = Problem.objects.create(
            question='What is $var1 + ${var2}?',
            variables_with_values = 'var1[1, 0, 10, 1], var2[1, 0, 10, 1]',
            answer='$var1 + ${var2}'
        )

    def test_problems_created(self):
        self.assertEqual(Problem.objects.count(), 2)

    def test_problem_without_vars(self):
        problem = Problem.objects.get(id=1)
        self.assertEqual(problem.calculate_answer(), 2.0)
        self.assertEqual(problem.calculated_answer, 2.0)
        self.assertEqual(problem.variables_as_lists, dict())
        self.assertEqual(problem.variables_as_floats, dict())
        self.assertEqual(problem.variables_as_strings, dict())
        self.assertTrue(problem.check_user_answer(2))

    def test_problem_with_vars(self):
        problem = Problem.objects.get(id=2)
        self.assertEqual(problem.calculate_answer(), 2.0)
        self.assertEqual(problem.calculated_answer, 2.0)
        self.assertEqual(
            problem.variables_as_lists, 
            {
                'var1': [1, 0, 10, 1],
                'var2': [1, 0, 10, 1],
            },
        )
        self.assertEqual(
            problem.variables_as_floats, 
            {
                'var1': 1.0,
                'var2': 1.0,
            },
        )
        self.assertEqual(
            problem.variables_as_strings, 
            {
                'var1': '1.0',
                'var2': '1.0',
            },
        )
        self.assertTrue(problem.check_user_answer(2))

    def test_problem_with_randomized_vars(self):
        problem = Problem.objects.get(id=2)
        problem.use_variables(problem.variables_randomized())
        new_vars = problem.variables_as_floats
        self.assertEqual(
            problem.variables_as_floats, 
            {
                'var1': new_vars['var1'],
                'var2': new_vars['var2'],
            },
        )
        self.assertEqual(
            problem.variables_as_strings, 
            {
                'var1': sn_round_str(new_vars['var1']),
                'var2': sn_round_str(new_vars['var2']),
            },
        )
        self.assertTrue(problem.check_user_answer(new_vars['var1'] + new_vars['var2']))
