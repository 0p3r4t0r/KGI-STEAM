from django.shortcuts import reverse
from django.test import Client, TestCase
from django.utils import timezone

from courses.models import Course, Problem, Syllabus, Worksheet
from courses.viewaids import kwargs_from_course, kwargs_from_course_and_worksheet


class CoursesViewTest(TestCase):
    def setUp(self):
        # Set the number of worksheets and problems to make.
        self.num_ws = 2
        self.problems_per_ws = 2
        # Create a course.
        course = Course.objects.create(
            year=timezone.now().year,
            name='Test MS Course',
            school='MS',
            nen=1,
            kumi='A',
        )
        # Create a syllabus
        Syllabus.objects.create(course=course)
        #Create some worksheets with problems.
        for i in range(0, self.num_ws):
            ws = Worksheet.objects.create(title='Test Worksheet {}'.format(i))
            course.worksheet_set.add(ws)
            for i in range(0, self.problems_per_ws):
                problem = Problem.objects.create(
                    question='What is the sum of $x and ${y}?',
                    variables_with_values='x[40], y[2]',
                    answer = '$x + ${y}', # Should evaluate to 42.
                )
                ws.problem_set.add(problem)
        self.test_course = Course.objects.first()
        self.test_ws = Worksheet.objects.first()
        self.test_course_kwargs = kwargs_from_course(Course.objects.first())
        self.test_ws_kwargs = kwargs_from_course_and_worksheet(
            self.test_course,
            self.test_ws,
        ) 


    def test_syllabus_view(self):
        kwargs = self.test_course_kwargs
        for i in range(0, 5):
            kwargs['term'] = 0
            response = self.client.get(
                reverse(
                    'courses:syllabus',
                    kwargs=kwargs,
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_worksheet_randomization(self):
        response = self.client.get(
            reverse('courses:worksheets-randomize', kwargs=self.test_ws_kwargs),
            follow=True,
        )
        self.assertEqual(
            response.redirect_chain[-1][0],
            reverse('courses:worksheets', kwargs=self.test_ws_kwargs),
        )

    def test_worksheet_view(self):
        response = self.client.get(
            reverse('courses:worksheets', kwargs=self.test_ws_kwargs)
        )
        self.assertEqual(response.status_code, 200)

    def test_worksheet_check_answers_view(self):
        problem = self.test_ws.problem_set.first()
        response = self.client.get(reverse('courses:worksheets-check-results'))
        # Test the check answers results view
        self.assertEqual(response.status_code, 200)
        # View with no POST returns a json response with result: 'invalid form'
        response = self.client.post(
            reverse('courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())
        self.assertEqual(dict(response.json())['result'], 'invalid form')
        # Check view returns result: 'correct'
        response = self.client.post(
            reverse('courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer }
        )
        self.assertEqual(dict(response.json())['result'], 'correct')
        # Check view return result: 'incorrect'
        response = self.client.post(
            reverse(
                'courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer + 1 }
        )
        self.assertEqual(dict(response.json())['result'], 'incorrect')

    def test_worksheet_reset_view(self):
        # Redirects back to the original worksheet.
        response = self.client.get(
            reverse('courses:worksheets-reset', kwargs=self.test_ws_kwargs),
            follow=True,
        )
        self.assertEqual(
            response.redirect_chain[-1][0],
            reverse('courses:worksheets', kwargs=self.test_ws_kwargs),
        )
        # Add some problems to the session.
        problem = self.test_ws.problem_set.first()
        self.client.post(
            reverse(
                'courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer }
        )
        self.client.post(
            reverse(
                'courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer + 1 }
        )
        # Check that the problems are cleared
        self.client.get(reverse('courses:worksheets-reset', kwargs=self.test_ws_kwargs))
        response = self.client.get(reverse('courses:worksheets-check-results'))
        for _ in self.test_ws.problem_set.all():
            self.assertNotIn(_.id, response.json()['checked_problems_correct'])
            self.assertNotIn(_.id, response.json()['checked_problems_incorrect'])

    def test_reset_all_view(self):
        problem = self.test_ws.problem_set.first()
        self.client.post(
            reverse(
                'courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer }
        )
        self.client.post(
            reverse(
                'courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer + 1 }
        )
        response = self.client.get(
            reverse('courses:worksheets-reset-all', kwargs=self.test_ws_kwargs),
            follow=True,
        )
        self.assertEqual(
            response.redirect_chain[-1][0],
            reverse('courses:worksheets', kwargs=self.test_ws_kwargs),
        )
        response = self.client.get(reverse('courses:worksheets-check-results'))
        self.assertEqual(response.json(), {'checked_problems_correct': [], 'checked_problems_incorrect': []})

    def test_resource_view(self):
        response = self.client.get(
            reverse('courses:resources', kwargs=self.test_course_kwargs)
        )
        self.assertEqual(response.status_code, 200)
