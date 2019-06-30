import os
import re
import sys

from django.apps import apps
from django.core.management import BaseCommand
from html.parser import HTMLParser


class HTMLChecker(HTMLParser):
    """ https://docs.python.org/3/library/html.parser.html
    """
 
    def handle_starttag(self, tag, attrs: list):
        self.check_attributes(tag, attrs)
        self.check_attribute_values(tag, attrs)
        self.check_django_tags(tag, attrs)

    def check_attributes(self, tag, attrs: list):
        attrs = [ attr[0] for attr in attrs ]
        self.is_sorted(tag, attrs, error_message='attribute order')    

    def check_attribute_values(self, tag, attrs: list):
        for attr in attrs:
            attr_name, attr_values = attr
            if attr_values is not None:
                attr_values = self.cut_django_tags(attr_values)
                attr_values = attr_values.split(' ')
                self.is_sorted(tag, attr_values, error_message='value order')

    def cut_django_tags(self, values: str) -> str:
        """ Remove the django tags from the string values.
        """
        django_tag = self.find_django_tag(values)
        while django_tag:
            values = values.replace(django_tag, '')
            django_tag = self.find_django_tag(values) 
        return values 

    def check_django_tags(self, tag, attrs: list):
        for attr in attrs:
            attr_name, attr_values = attr
            if attr_values is not None:
                django_tags = []
                django_tag = self.find_django_tag(attr_values)
                while django_tag:
                    django_tags.append(django_tag)
                    attr_values = attr_values.replace(django_tag, '')
                    django_tag = self.find_django_tag(attr_values)
                self.is_sorted(tag, django_tags, 'django tag order')
    
    def find_django_tag(self, values: str) -> str:
        """ Get the django tags from a string.
        """
        DJANGO_TAG = '^.*(\{%[^\%}]+\%}).*'
        django_tag = re.match(DJANGO_TAG, values)
        if django_tag:
            return django_tag.group(1)

    def is_sorted(self, tag, html: list, error_message: str):
        """ Checks if a list is sorted.
        """
        FORMAT_STR = '\tline {position} {tag}: {error_message}\n\t\tchange: {html}\n\t\tto:     {html_sorted}\n'
        html_sorted = sorted(html)
        if html != html_sorted:
            line_number, line_spaces = self.getpos()
            print(FORMAT_STR.format(position=line_number, tag=tag,
                    error_message=error_message,
                    html=html, html_sorted=html_sorted))


class Command(BaseCommand):
    """ Checks that the templates adhere to the conventions.

    * Here alphabetical order is defined by the sorted() BIF.

    1. Attributes are in alphabetical order.
    2. Attribute valies are in alphabetical order.
    3. There should be four space indents.
    
    """
    help = 'Checks that html agrees with the conventions in the docs.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label', nargs='*',
            help='Specify the app(s) whose templates you want to check.'
        )

    def handle(self, *app_labels, **options):
        app_labels = set(app_labels)
        has_bad_labels = False
        for app_label in app_labels:
            """ Check that the app exists."""
            try:
                apps.get_app_config(app_label)
            except LookupError as err:
                self.stderr.write(str(err))
                has_bad_labels = True
        if has_bad_labels: 
            sys.exit(2)
        
        for app_label in app_labels:
            """ Check that the templates dir exists."""
            template_base = self.template_base_dir(app_label)
            if not os.path.exists(template_base):
                self.stderr.write('Directory not found: {}'.format(template_base))
                sys.exit(2)

        checker = HTMLChecker()
        for app_label in app_labels:
            """ Check the html"""
            for file_path in self.template_file_paths(app_label):
                print('checking file: {}'.format(file_path))
                with open(file_path) as f:
                    for line in f:
                        checker.feed(line)


    def template_base_dir(self, app_label):
        return os.path.join(app_label, 'templates', app_label)

    def template_file_paths(self, app_label):
        template_base = self.template_base_dir(app_label)
        # https://docs.python.org/3/library/os.html?highlight=os#os.walk
        file_paths = []
        for dir_path, subdirs, file_names in os.walk(template_base):
            file_paths += [ os.path.join(dir_path, file_name)
                        for file_name in file_names
                        if file_name.endswith('html') ] 
        return file_paths
           
