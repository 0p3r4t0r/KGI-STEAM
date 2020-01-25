from django.urls import path

from . import views

courses_url = '<int:year>/<school>/<name>/<nen_kumi>'

urlpatterns = [
    path('', views.courses_home, name='courses-home'),
    # Syllabi
    path('{}/syllabus'.format(courses_url),
        views.syllabus,
        name='course-syllabi',
    ),
    # Worksheets
    path('{}/worksheets/<worksheet_title>/<order>'.format(courses_url),
        views.worksheets,
        name='course-worksheets',
    ),
    path('worksheets/problems/check/results',
        views.worksheets_check_answer_results,
        name='course-worksheets-check-results',
    ),
    path('worksheets/problems/check/<problem_id>',
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
    # Resources
    path('{}/resources'.format(courses_url),
        views.resources,
        name='course-resources',
    ),
]
