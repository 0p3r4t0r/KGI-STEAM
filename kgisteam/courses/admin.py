from markdownx.widgets import AdminMarkdownxWidget

from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from courses.forms import ProblemAdminForm
from courses.models import Course, CourseResource, Lesson, Problem, SharedResource, Syllabus, Worksheet


class CourseResourceInline(admin.StackedInline):
    extra = 0
    model = CourseResource


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    https://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
    https://docs.djangoproject.com/en/2.2/ref/utils/#module-django.utils.html
    """
    inlines = [CourseResourceInline,]
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
    extra = 0
    model=Lesson


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    inlines = [LessonInline,]
    list_display = ('course',)


class ProblemInline(admin.StackedInline):
    extra = 0
    form = ProblemAdminForm
    model = Problem


@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    """
    https://neutronx.github.io/django-markdownx/customization/#fields
    """
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }
    inlines = [ProblemInline,]
    filter_horizontal = ('course',)
    list_display = ('title',)


@admin.register(SharedResource)
class ResourceAdmin(admin.ModelAdmin):
    filter_horizontal = ('courses',)
