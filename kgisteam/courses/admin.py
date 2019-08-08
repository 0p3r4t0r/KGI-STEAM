from django.contrib import admin
from django.utils.html import format_html

from courses.models import Course, Lesson, Syllabus


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    https://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
    https://docs.djangoproject.com/en/2.2/ref/utils/#module-django.utils.html
    """
    list_display = ('name', 'school', 'nen_kumi', 'year')    

    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return format_html('<img src="{}" width="{}" height={} />',
            obj.image_path.url,
            200,
            200,
        )


class LessonInline(admin.StackedInline):
    """
    https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#inlinemodeladmin-objects
    """
    model=Lesson


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    inlines = [LessonInline,]
    list_display = ('course',)
