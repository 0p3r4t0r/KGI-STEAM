from django.test import TestCase

from courses.models import Course, Problem, Resource, Syllabus, Worksheet


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
        self.assertEqual(len(Course.objects.all()), 2)
    
    def test_courses_nen_kumi_field(self):
        self.assertEqual(self.hs_course.nen_kumi, '1-1')
        self.assertEqual(self.ms_course.nen_kumi, '1-A')

class TestProblem(TestCase):
    def setUp(self):
        pass

class TestResource(TestCase):
    def setUp(self):
        pass

class TestSyllabus(TestCase):
    def setUp(self):
        pass

class TestWorksheet(TestCase):
    def setUp(self):
        pass

