from django.urls import path

from . import views

courses_url = '<school>/<name>/<nen_kumi>/<int:year>'

urlpatterns = [
    path('', views.courses_home, name='courses-home'),
    # Syllabi
    path('{}/syllabus'.format(courses_url),
        views.CourseView.as_view(template_name='courses/course_syllabus.html'),
        name='course-syllabi',
    ),
    # Worksheets
    path('{}/worksheets/<worksheet_title>/<order>'.format(courses_url),
        views.CourseView.as_view(template_name='courses/course_worksheets.html'),
        name='course-worksheets',
    ),
    path('{}/worksheets/<worksheet_title>/<order>/check/<problem_id>'.format(courses_url),
        views.worksheets_check_answer,
        name='course-worksheets-check',
    ),
    path('{}/worksheets/<worksheet_title>/<order>/reset'.format(courses_url),
        views.worksheets_reset,
        name='course-worksheets-reset',
    ),
    path('{}/worksheets/<worksheet_title>/<order>/resetall'.format(courses_url),
        views.worksheets_reset_all,
        name='course-worksheets-reset-all',
    ),
    path('{}/worksheets/<worksheet_title>/<order>/shuffle'.format(courses_url),
        views.worksheets_problems_order,
        name='course-worksheets-problems-order',
    ),
    # Resources
    path('{}/resources'.format(courses_url),
        views.CourseView.as_view(template_name='courses/course_resources.html'),
        name='course-resources',
    ),
]
