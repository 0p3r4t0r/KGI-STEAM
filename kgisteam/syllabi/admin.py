from django.contrib import admin

from syllabi.models import Lesson, Syllabus


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('course',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass
