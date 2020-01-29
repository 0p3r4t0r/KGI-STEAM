from django.shortcuts import reverse
from django.test import Client, TestCase
from django.utils import timezone

from courses.models import Course, Syllabus, Worksheet
from courses.viewaids import kwargs_from_course


class CoursesViewTest(TestCase):
    def setUp(self):
        num_ws = 5
        # Create a course.
        course1 = Course.objects.create(
            year=timezone.now().year,
            name='Test MS Course',
            school='MS',
            nen=1,
            kumi='A',
        )
        # Create a syllabus
        Syllabus.objects.create(course=course1)
        #Create some worksheets
        for i in range(0, 5):
            ws = Worksheet.objects.create(title='Test Worksheet {}'.format(i))
            course1.worksheet_set.add(ws)

    def test_create_worksheets(self):
        self.assertEqual(len(Worksheet.objects.all()), 5)

    def test_syllabus_view(self):
        course = Course.objects.first()
        client = Client()
        response = client.get(
            reverse(
                'courses:syllabus',
                kwargs=kwargs_from_course(course)
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_worksheet_view(self):
        ws = Worksheet.objects.first()
        client = Client()
        kwargs = kwargs_from_course(ws.course.first())
        kwargs['title'] = ws.title
        kwargs['order'] = 'ordered'
        response = client.get(reverse('courses:worksheets', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)


    def test_worksheet_view(self):
        course = Course.objects.first()
        client = Client()
        response = client.get(
            reverse(
                'courses:resources',
                kwargs=kwargs_from_course(course)
            )
        )
        self.assertEqual(response.status_code, 200)
