from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'branch', 'parent_phone', 'created_at')
    list_filter = ('branch',)
    search_fields = ('first_name', 'last_name', 'phone', 'parent_name', 'parent_phone')

    fieldsets = (
        ('Особисті дані', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth')}),
        ('Контакти батьків', {'fields': ('parent_name', 'parent_phone', 'parent_email')}),
        ('Гілка', {'fields': ('branch',)}),
    )
