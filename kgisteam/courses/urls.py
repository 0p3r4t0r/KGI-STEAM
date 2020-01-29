from django.urls import path

from . import views
app_name = 'courses'
courses_base_url = '<int:year>/<school>/<name>/<nen_kumi>'

urlpatterns = [
    path('', views.courses_home, name='home'),
    # Syllabi
    path('{}/syllabus'.format(courses_base_url),
        views.syllabus,
        name='syllabus',
    ),
    # Worksheets
    path('{}/worksheets/<title>/<order>'.format(courses_base_url),
        views.worksheets,
        name='worksheets',
    ),
    path('worksheets/problems/check/results',
        views.worksheets_check_answer_results,
        name='worksheets-check-results',
    ),
    path('worksheets/problems/check/<problem_id>',
        views.worksheets_check_answer,
        name='worksheets-check',
    ),
    path('{}/worksheets/<title>/<order>/reset'.format(courses_base_url),
        views.worksheets_reset,
        name='worksheets-reset',
    ),
    path('{}/worksheets/<title>/<order>/resetall'.format(courses_base_url),
        views.worksheets_reset_all,
        name='worksheets-reset-all',
    ),
    # Resources
    path('{}/resources'.format(courses_base_url),
        views.resources,
        name='resources',
    ),
]
