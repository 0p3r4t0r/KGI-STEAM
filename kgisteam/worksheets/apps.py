from django.apps import AppConfig


class WorksheetsConfig(AppConfig):
    description = ('Practice what you learned: '
        'in class, at home, or anywhere in between.'
        )                            
    icon_path = 'worksheets/icons/worksheetsConfigIcon.svg'                           
    name = 'worksheets'
