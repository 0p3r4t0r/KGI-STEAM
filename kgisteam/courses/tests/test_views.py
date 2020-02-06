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
                self.assertEqual(problem.calculated_answer, 42)
            self.assertEqual(len(ws.problem_set.all()), self.problems_per_ws)

    def test_calculate_answer(self):
        pass

    def test_problem_variables(self):
        pass

    def test_problem_randomization(self):
        pass

    def test_syllabus_view(self):
        course = Course.objects.first()
        response = self.client.get(
            reverse(
                'courses:syllabus',
                kwargs=kwargs_from_course(course)
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_worksheets_created(self):
        self.assertEqual(len(Worksheet.objects.all()), self.num_ws)

    def test_worksheet_randomization(self):
        course = Course.objects.first()
        ws = Worksheet.objects.first()
        ws_kwargs = kwargs_from_course_and_worksheet(course, ws) 
        courses_worksheets_url = reverse('courses:worksheets', kwargs=ws_kwargs)
        # Ensure that you end up back at worksheets.
        response = self.client.get(
            reverse('courses:worksheets-randomize', kwargs=ws_kwargs),
            follow=True,
        )
        self.assertEqual(
            response.redirect_chain[-1][0],
            courses_worksheets_url,
        )

    def test_worksheet_view(self):
        course = Course.objects.first()
        ws = Worksheet.objects.first()
        ws_kwargs = kwargs_from_course_and_worksheet(course, ws) 
        courses_worksheets_url = reverse('courses:worksheets', kwargs=ws_kwargs)
        # Test a worksheet view
        response = self.client.get(courses_worksheets_url)
        self.assertEqual(response.status_code, 200)
        # Test the check answers results view
        problem = ws.problem_set.first()
        response = self.client.get(reverse('courses:worksheets-check-results'))
        self.assertEqual(response.status_code, 200)
        # problem check view returns a json response with result: 'invalid form'
        response = self.client.post(
            reverse('courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json())
        self.assertEqual(dict(response.json())['result'], 'invalid form')
        # problem check view returns result: 'correct'
        response = self.client.post(
            reverse('courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer }
        )
        self.assertEqual(dict(response.json())['result'], 'correct')
        # problem check view return result: 'incorrect'
        response = self.client.post(
            reverse('courses:worksheets-check',
                kwargs={ 'problem_id': problem.id }
            ),
            { 'user_answer': problem.calculated_answer + 1 }
        )
        self.assertEqual(dict(response.json())['result'], 'incorrect')
        # Test the reset view
        response = self.client.get(
            reverse('courses:worksheets-reset', kwargs=ws_kwargs),
            follow=True,
        )
        self.assertEqual(
            response.redirect_chain[-1][0],
            courses_worksheets_url,
        )
        response = self.client.get(reverse('courses:worksheets-check-results'))
        for _ in ws.problem_set.all():
            self.assertNotIn(_.id, response.json()['checked_problems_correct'])
            self.assertNotIn(_.id, response.json()['checked_problems_incorrect'])
        # Test the reset_all view
        response = self.client.get(
            reverse('courses:worksheets-reset-all', kwargs=ws_kwargs),
            follow=True,
        )
        self.assertEqual(
            response.redirect_chain[-1][0],
            courses_worksheets_url,
        )
        response = self.client.get(reverse('courses:worksheets-check-results'))
        self.assertEqual(response.json(), {'checked_problems_correct': [], 'checked_problems_incorrect': []})

    def test_resource_view(self):
        course = Course.objects.first()
        response = self.client.get(
            reverse(
                'courses:resources',
                kwargs=kwargs_from_course(course)
            )
        )
        self.assertEqual(response.status_code, 200)
