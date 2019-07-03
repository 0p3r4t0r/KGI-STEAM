from django.apps import AppConfig


class SyllabiConfig(AppConfig):
    description = ( 'Course content and plans: ' 
        'assignments, due dates, links, etc. '
        )                            
    icon_path = 'syllabi/icons/syllabiConfigIcon.svg'                           
    name = 'syllabi'
