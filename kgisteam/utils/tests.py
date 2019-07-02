from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class ChecktemplatesTest(TestCase):
    def test_command_output(self):
        out = StringIO()
        call_command('checktemplates', 'utils',stdout=out)
        attribute_order_warning = 'line 3 section: attribute order'
        value_order_warning = 'line 4 div: value order'
        djtag_order_warning = 'line 6 img: django tag order'
        
        print(out.getvalue())
        self.assertIn(attribute_order_warning, out.getvalue())
        self.assertIn(value_order_warning, out.getvalue())
        self.assertIn(djtag_order_warning, out.getvalue())
