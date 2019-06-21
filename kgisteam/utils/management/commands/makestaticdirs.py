import sys
import os

from django.apps import apps
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """ Creates directories for static files if they don't exist.

       
        https://github.com/django/django/blob/master/django/core/management/commands/makemigrations.py
        https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/#accepting-optional-arguments"
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_dirs = [ 'css', 'css/scss', 'images', 'js' ]

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label', nargs='*',
            help='Specify the label(s) to make static directories for.',
        )
        parser.add_argument(
            '--check', action='store_true',
            help='Check if static directories math the convention from the docs.',
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

        if app_labels and not options['check']:
            for app_label in app_labels:
                self.make_static_dirs(app_label)

        if options['check']:
            for app_label in app_labels:
                self.check_static_dirs(app_label)

    def check_static_dirs(self, app_label):
        for static_dir_path in self.static_dir_paths(app_label):
            if not os.path.isdir(static_dir_path):
                print('directory not found: {}'.format(static_dir_path))
        ''' 
        dirs_in_app = os.listdir(app_label)
        if (set(self.static_dirs).intersection(set(dirs_in_app)) !=
            set(self.static_dirs)):
            print('missing') 
        '''

    def make_dir(self, path):
        try:
            os.makedirs(path)
            print('directory created: {}'.format(path))
        except FileExistsError:
            print('directory already exists: {}'.format(path))
        except OSError:
            print('failed to create directory: {}'.format(path))

    def static_dir_paths(self, app_label):
        static_base = os.path.join(app_label, 'static', app_label)
        static_dir_paths = [ os.path.join(static_base, static_dir) 
                                for static_dir in self.static_dirs ]
        static_dir_paths.insert(0, static_base)
        return static_dir_paths

    def make_static_dirs(self, app_label):
        for static_dir_path in self.static_dir_paths(app_label):
            self.make_dir(static_dir_path)
