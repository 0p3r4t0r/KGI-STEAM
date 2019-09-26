from django.test import TestCase

# Create your tests here.
def spaced_print(content: str) -> str:
    "just for debugging"
    spacer = '\n' * 4
    print(spacer + str(content) + spacer)
