import os
import sys

from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Checking attributes:
    1. Find the tags.
    2. Get attributes in the order they appear in the files.
    3. sort the atributes alphabetically.
    4. Check that 2. and 3. are equal, if not the test fails.

    Checking ((the things inside the attributes)).

    Checking indentation.


    Bonus features
    check that custom tags end with a single underscore.
    """
    help = 'Checks that html agrees with the conventions in the docs.'
    
    def add_arguments(self, *args, **options):
        pass

    def handle(self, *args, **options):
        pass 
