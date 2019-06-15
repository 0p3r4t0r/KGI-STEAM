from django.db import models


class Course(models.Model):
    """Store course information.
    
    course_name --> You should be careful about support for Japanese.
    course_image --> an optional field to add and image for your course.
    course_grade --> choose ms/hs and year.
    course_class --> select from a list of possible classes. Make this easy to change.
    
    course_syllabus --> relation? separate app?
    course_worksheets --> relation? separate app?
    """

    pass
