from martor.models import MartorField
from martor.widgets import AdminMartorWidget

from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from courses.forms import CourseAdminForm, ProblemInlineForm
from courses.models import Course, Lesson, Problem, Resource, Syllabus, Worksheet


class CoursesBaseAdmin(admin.ModelAdmin):
    pass

    class Meta:
        abstract = True


@admin.register(Course)
class CourseAdmin(CoursesBaseAdmin):
    """
    https://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
    https://docs.djangoproject.com/en/2.2/ref/utils/#module-django.utils.html
    """
    form = CourseAdminForm
    list_display = ('name', 'school', 'nen_kumi', 'year')
    readonly_fields = ("image_preview",)
    search_fields = ('name', 'nen_kumi', 'year')

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
    model = Lesson


@admin.register(Syllabus)
class SyllabusAdmin(CoursesBaseAdmin):
    inlines = [LessonInline,]
    list_display = ('course',)
    search_fields = ('course__name',)


class ProblemInline(admin.StackedInline):
    extra = 0
    form = ProblemInlineForm
    model = Problem
    formfield_overrides = {
        MartorField: {'widget': AdminMartorWidget},
    }
    readonly_fields = ("calculated_answer",)


@admin.register(Worksheet)
class WorksheetAdmin(CoursesBaseAdmin):
    inlines = [ProblemInline,]
    filter_horizontal = ('course',)
    list_display = ('title',)
    search_fields = ('description', 'title')


@admin.register(Resource)
class ResourceAdmin(CoursesBaseAdmin):
    filter_horizontal = ('courses',)
    search_fields = ('category', 'description', 'link_text')
