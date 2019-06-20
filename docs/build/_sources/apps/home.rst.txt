home
====

All this app is meant to do is display the home page, and hold base template
files. A base template file is any template that could be used site-wide.


home/templates:

base.html
  The base template for the entire site. All other templates shoule extend
  this template.

  .. code-block:: python3

     {% extends 'home/base.html' %}


home.html
  The actual homepage for the site. This page displays the course cards
  and the newsfeed.


_navbar.html
  The navbar for the site. This should also be used on almost every page.
  The underscore prefix in the name indicated that the template is meant
  to be included in other templates.

  .. code-block:: python3

     {% include 'home/_navbar.html' %}
