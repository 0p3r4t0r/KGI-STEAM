from django.test import TestCase
from django.utils import timezone

from courses.models import Course, Lesson, Syllabus


class TestTerms(TestCase):
    def setUp(self):
        self.term_timedelta = timezone.timedelta(weeks=12)

        course = Course.objects.create(
                term1_start = timezone.now(),
                term2_start = timezone.now() + self.term_timedelta,
                term3_start = timezone.now() + 2 * self.term_timedelta,
                term4_start = timezone.now() + 3 * self.term_timedelta,
                name='Test HS Course',
                school='HS',
                nen='1',
                kumi='1',
        )
        syllabus = Syllabus.objects.create(
            course=course
        )
        for i in range(0, 8):
            Lesson.objects.create(
                syllabus=syllabus,
                number = i,
                date = timezone.now()
            )


    def test_course_term_now(self):

        def rewind_starts(course, timedelta):
            course.term1_start = course.term1_start - timedelta
            course.term2_start = course.term2_start - timedelta
            course.term3_start = course.term3_start - timedelta
            course.term4_start = course.term4_start - timedelta
            return course

        course = Course.objects.get(id=1)
        for i in range(0, 4):
            course = rewind_starts(course, i * self.term_timedelta)
            self.assertEqual(course.term_now, i + 1)

    def test_course_term_type(self):
        course = Course.objects.get(id=1)
        course.term1_start = ''
        course.term2_start = ''
        course.term3_start = ''
        course.term4_start = ''
        self.assertIsNone(course.term_type)
        course.term1_start = timezone.now()
        self.assertIsNone(course.term_type)
        course.term2_start = course.term1_start + self.term_timedelta
        self.assertEqual(course.term_type, 'semesters')
        course.term3_start = course.term1_start + 2 * self.term_timedelta
        self.assertEqual(course.term_type, 'trimesters')
        course.term4_start = course.term1_start + 3 * self.term_timedelta
        self.assertEqual(course.term_type, 'quarters')

    def test_lesson_term_num(self):
        lessons = Lesson.objects.all()
        for lesson in lessons:
            self.assertEqual(lesson.term_num, 1)
        for i in range(0, 4):
            for lesson in lessons[2*i:2*i+2]:
                lesson.date += i*self.term_timedelta
                self.assertEqual(lesson.term_num, i+1)
