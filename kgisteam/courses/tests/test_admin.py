from django.shortcuts import reverse
from django.test import Client, TestCase
from django.utils import timezone

from courses.models import Course, Problem, Syllabus, Worksheet
from courses.viewaids import kwargs_from_course, kwargs_from_course_and_worksheet
from users.models import CustomUser


class AdminViewTest(TestCase):
    def setUp(self):
        # Create a superuser
        super_user_pass = 'NotPassword123'
        super_user = CustomUser.objects.create_superuser(
            username='test.super',
            password=super_user_pass,
        )
        # Test login
        login = self.client.login(
            username=super_user.username,
            password=super_user_pass
        )
        self.assertTrue(login)

    def test_course_views(self):
        url_names = [ 'admin:index' ]
        actions = [ 'changelist', 'add' ]
        app_models = { 
            'courses': [ 'course', 'resource', 'syllabus', 'worksheet'],
            'taggit': [ 'tag' ], 
            'users': [ 'customuser' ],
        }
        for app, models in app_models.items():
            for model in models:
                for action in actions:
                    url_names.append('admin:{app}_{model}_{action}'.format(app=app, model=model, action=action))
        for url_name in url_names:
            request = self.client.get(reverse(url_name))
            self.assertEqual(request.status_code, 200)
