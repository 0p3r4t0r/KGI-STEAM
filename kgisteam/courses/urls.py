from django.urls import path

from . import views

courses_url = '<school>/<name>/<nen_kumi>/<int:year>'

urlpatterns = [
    path('', views.courses_home, name='courses-home'),
    path('{}/syllabus'.format(courses_url),
        views.CourseView.as_view(template_name='courses/course.html'),
        name='course-syllabi',
    ),
    path('{}/worksheets'.format(courses_url),
        views.CourseView.as_view(template_name='courses/course.html'),
        name='course-worksheets',
    ),
    path('{}/resources'.format(courses_url),
        views.CourseView.as_view(template_name='courses/course.html'),
        name='course-resources',
    ),
]
