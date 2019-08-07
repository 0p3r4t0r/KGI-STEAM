from django.urls import path

from . import views


urlpatterns = [
    path('', views.courses_home, name='courses-home'),
    path('<school>/<name>/<class>/<int:year>',
        views.CourseView.as_view(template_name='courses/course.html'),
        name='courses-course',
    ),
]
