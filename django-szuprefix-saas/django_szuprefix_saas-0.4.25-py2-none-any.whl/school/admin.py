# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models, helper

@admin.register(models.School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)
    readonly_fields = ('party',)


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school",)
    search_fields = ("school__name",)
    readonly_fields = ('party',)


@admin.register(models.College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", 'code')
    raw_id_fields = ("party", "school")
    search_fields = ("school__name", "name")
    readonly_fields = ('party',)


@admin.register(models.Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ("name", 'code')
    raw_id_fields = ("party", "school")
    search_fields = ("school__name", "name")
    readonly_fields = ('party',)


@admin.register(models.Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school",)
    search_fields = ("school__name",)
    readonly_fields = ('party',)


@admin.register(models.Clazz)
class ClazzAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school", "entrance_session", "graduate_session", "primary_teacher", "grade")
    search_fields = ("school__name", "name")
    readonly_fields = ('party',)



def unbind_student(modeladmin, request, queryset):
    for student in queryset.all():
        helper.unbind(student)


unbind_student.short_description = u"解除绑定"


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('school', "name", 'number', 'clazz', 'create_time')
    list_filter = ('school',)
    list_select_related = ('school', 'clazz')
    raw_id_fields = ("school", "entrance_session", "graduate_session", "grade", 'party', 'school', 'user', 'clazz')
    search_fields = ("school__name", 'name', 'number')
    readonly_fields = ('party',)
    actions = [unbind_student]


@admin.register(models.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school", 'party', 'user')
    search_fields = ("school__name", 'name')
    readonly_fields = ('party',)


@admin.register(models.ClazzCourse)
class ClazzCourseAdmin(admin.ModelAdmin):
    list_display = ("clazz", "course", "teacher")
    list_select_related = ("clazz", "course", "teacher")
    search_fields = ('clazz__name', "course__name")
    raw_id_fields = ('clazz', 'course', 'teacher')
    # readonly_fields = ('party',)

