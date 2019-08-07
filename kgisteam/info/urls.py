from django.urls import path

from . import views


urlpatterns = [
    path('', views.info_home, name='info-home'),
]
