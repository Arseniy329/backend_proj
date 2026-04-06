from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'branch', 'status', 'parent_phone', 'created_at')
    list_filter = ('status', 'branch')
    search_fields = ('first_name', 'last_name', 'phone', 'parent_name', 'parent_phone')
    actions = ['archive_selected', 'restore_selected']

    fieldsets = (
        ('Особисті дані', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')}),
        ('Контакти батьків', {'fields': ('parent_name', 'parent_phone', 'parent_email')}),
        ('Гілка та статус', {'fields': ('branch', 'status')}),
    )

    @admin.action(description='Архівувати обраних')
    def archive_selected(self, request, queryset):
        queryset.update(status=Student.Status.ARCHIVED)

    @admin.action(description='Відновити обраних')
    def restore_selected(self, request, queryset):
        queryset.update(status=Student.Status.ACTIVE)
