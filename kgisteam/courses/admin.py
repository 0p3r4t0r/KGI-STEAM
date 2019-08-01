from django.contrib import admin
from django.utils.safestring import mark_safe

from courses.models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    https://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
    """    
    list_display = ('name', 'school', 'grade', 'letter_number')    

    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.headshot.url,
            width=obj.headshot.width,
            height=obj.headshot.height,
            )
        )
