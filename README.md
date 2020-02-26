# KGI STEAM
The name is a combination of an abbreviation for Kogakuin 
(the school where I used to work) and the 
acronym [STEAM](https://en.wikipedia.org/wiki/STEAM_fields).

This software was developed to automate the repetative tasks 
that go along with being a teacher, with the ultimate goal being to reduce
the number of working hours required per week to a reasonable amount.

The vast majority of the code was written off-the-cuff during meetings
and so this certainly wasn't intended to be robust piece of
software by any means. However, more often than not what matters at the
end of the day (especially in regards to personal projects), is whether 
or not your code was effective and I can say that having KGI STEAM as a
cirriculum management system did greatly reduce the amount of time it
took to prepare, organize and distribute lesson materials.

It's far from perfect, but it's good enough and overall I'm proud of what I've done here.
At present I don't plan to use the site ever again, but I'm leaving it here in case
someone else finds it useful.


## Table of Contents
* [Features](#Features)
* [Tech Stack](#Tech-Stack)
* [Deployment](#Deployment)




## Features
The site is designed to allow students to practice solving problems. It requires no login,
so students don't have to remember another set of login credentials.

### For students
* Try a problem and check it instantly.
* Randomize the numbers in your problems and try again.

### For teachers
* Use the syllabus to remind students what's going on in class.
* Worksheets allow you to render mathematical equations on the web.
* Resources allow students to quickly navigate to any external links you may need for class.




## Tech Stack
*  [Python Anywhere](https://www.pythonanywhere.com/)
*  [Django 3.0](https://docs.djangoproject.com/en/3.0/)
*  [Bulma CSS](https://bulma.io/)

### Shoutouts to...
*   [MathJax](https://www.mathjax.org/)
    for rendering my math equations.

*   [Martor](https://github.com/agusmakmun/django-markdown-editor)
    for creating an awesome interface to preview and edit markdown
    (and for pulling my commits).

*   [Icons8](https://icons8.com/) 
    for inspiring the logo and providing the base SVG files.

*   [Real Favicon Generator](https://realfavicongenerator.net/)
    for generating the favicons, 

*   [Unsplash](https://unsplash.com/search/photos/open-source)
    for providing the images for the courses.




## Deployment
1. Create a python virtual environment.
2. From within your virtual env run `pip install -r requirements.txt`
3. Try running `manage.py runserver`, if that doesn't work follow the
   instructions printed in the error message and setup a .env_settings file.
4. Apply the migrations `manage.py migrate`.
