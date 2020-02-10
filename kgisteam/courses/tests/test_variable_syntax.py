from django.test import TestCase
from django.utils import timezone

from courses.maths import sn_round_str
from courses.models import Course, Lesson, Problem, Resource, Syllabus, Worksheet


class TestProblem(TestCase):
    def setUp(self):
        """ Create problems with different variables_with_values.
        https://docs.djangoproject.com/en/3.0/topics/db/queries/#copying-model-instances
        """
        self.test_problem = Problem.objects.create(
            question='What is $var1 + ${var2}?',
            variables_with_values='var1[1], var2[2]',
            answer='$var1 + ${var2}'
        )

    def test_vars_defaults(self):
        problem = Problem.objects.get(id=1)
        self.assertFalse(problem.is_randomizable)
        self.assertEqual(
            problem.variables_randomized(),
            problem.variables_as_floats,
        )

    def test_vars_mins(self):
        problem = Problem.objects.get(id=1)
        problem.variables_with_values = 'var1[1, 6], var2[2, 7]'
        self.assertTrue(problem.is_randomizable)
        randomized_vars = problem.variables_randomized()
        for key, value in randomized_vars.items():
            self.assertAlmostEqual(
                problem.variables_as_floats[key],
                value,
                delta=5,
            )

    def test_vars_min_max(self):
        problem = Problem.objects.get(id=1)
        problem.variables_with_values = 'var1[1, -4, 6], var2[2, -3, 7]'
        self.assertTrue(problem.is_randomizable)
        randomized_vars = problem.variables_randomized()
        for key, value in randomized_vars.items():
            self.assertAlmostEqual(
                problem.variables_as_floats[key],
                value,
                delta=10,
            )

    def test_vars_is_int(self):
        problem = Problem.objects.get(id=1)
        problem.variables_with_values = 'var1[1, -4, 6, 0], var2[2, -3, 7, 1]'
        self.assertTrue(problem.is_randomizable)
        randomized_vars = problem.variables_randomized()
        for key, value in randomized_vars.items():
            self.assertAlmostEqual(
                problem.variables_as_floats[key],
                value,
                delta=10,
            )
        self.assertIsInstance(randomized_vars['var1'], float)
        self.assertIsInstance(randomized_vars['var2'], int)
