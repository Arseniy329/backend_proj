from django.contrib import admin

from .models import Branch, Subject, Group, SubscriptionPlan, Lesson, Attendance


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address', 'status', 'created_at')
    list_filter = ('status', 'city')
    search_fields = ('name', 'city', 'address')
    actions = ['archive_selected', 'restore_selected']

    @admin.action(description='Архівувати обраних')
    def archive_selected(self, request, queryset):
        queryset.update(status=Branch.Status.ARCHIVED)

    @admin.action(description='Відновити обраних')
    def restore_selected(self, request, queryset):
        queryset.update(status=Branch.Status.ACTIVE)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)
    filter_horizontal = ('branches',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'subject', 'teacher', 'status', 'created_at')
    list_filter = ('status', 'branch', 'subject')
    search_fields = ('name',)
    filter_horizontal = ('students',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'lessons_count', 'price', 'duration_days', 'branch', 'created_at')
    list_filter = ('branch',)
    search_fields = ('name',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('group', 'teacher', 'date', 'start_time', 'end_time', 'status', 'created_at')
    list_filter = ('status', 'date', 'group__branch')
    search_fields = ('topic', 'group__name')
    date_hierarchy = 'date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'status', 'created_at')
    list_filter = ('status', 'lesson__date')
    search_fields = ('student__first_name', 'student__last_name')
