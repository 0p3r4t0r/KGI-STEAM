from django.test import TestCase
from django.utils import timezone

from courses.models import Course


class CourseModelTest(TestCase):
    def setUp(self):
        # Create MS Course
        Course.objects.create(
            year=timezone.now().year,
            name='Test MS Course',
            school='MS',
            nen=1,
            kumi='A',
        )
        # Create HS Course
        Course.objects.create(
            year=timezone.now().year,
            name='Test HS Course',
            school='HS',
            nen=1,
            kumi='1',
        )
        self.course1 = Course.objects.first()
        self.ms_course1 = Course.objects.filter(
            school='MS').first()
        self.hs_course1 = Course.objects.filter(
            school='HS').first()

    def test_create_course(self):
        self.assertIsInstance(self.course1, Course)
