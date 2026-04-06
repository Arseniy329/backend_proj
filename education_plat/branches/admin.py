from django.contrib import admin

from .models import Branch, Subject, Group


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'status', 'created_at')
    list_filter = ('status', 'city')
    search_fields = ('name', 'city', 'address')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('branches',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'subject', 'teacher', 'status', 'created_at')
    list_filter = ('status', 'branch', 'subject')
    search_fields = ('name',)
    filter_horizontal = ('students',)
