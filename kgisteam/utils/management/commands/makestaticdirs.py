import sys

from os.path import isdir

from django.apps import apps
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """ Creates directories for static files if they don't exist.

       
        https://github.com/django/django/blob/master/django/core/management/commands/makemigrations.py
        https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/#accepting-optional-arguments"
    """
    
    # directory: if exists --> 1 else --> 0
    dirs_exists = { 'css': 0, 'css/scss': 0, 'images': 0, 'js': 0 }

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label', nargs='*',
            help='Specify the label(s) to make static directories for.',
        )

    def handle(self, *app_labels, **options):
        app_labels = set(app_labels)
        has_bad_labels = False
        for app_label in app_labels:
            try:
                apps.get_app_config(app_label)
            except LookupError as err:
                self.stderr.write(str(err))
                has_bad_labels = True
        if has_bad_labels:
            sys.exit(2)

        if app_labels:
            self.make_dirs()

    def make_dirs(self, dirs=None):
        if dirs is None:
            dirs = self.dirs_exists
        '''
            1. Check if every dir exists.
            2. If it doesn't exists, create it.
        '''
        print(dirs) 
            
      
