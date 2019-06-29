#!/usr/bin/env python
# https://docs.python.org/3/library/html.parser.html

import sys

from html.parser import HTMLParser


file_path = sys.argv[1]


class HTMLChecker(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs_sorted = sorted(attrs)
        if attrs != attrs_sorted:
            print('Attributes out of order: {}'.format(tag))
            print(attrs)
            print(attrs_sorted)
        for attr in attrs:
            attr_name = attr[0]
            attr_values = attr[1].split(' ')
            attr_values_sorted = sorted(attr_values)
            if attr_values != attr_values_sorted:
                print('Values out of order: {}'.format(attr_name))
                print(attr_values)
                print(attr_values_sorted)

checker = HTMLChecker()
with open(file_path) as f:
    for number, line in enumerate(f):
        checker.feed(line)
