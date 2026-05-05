import django_filters

from .models import Student


class StudentFilter(django_filters.FilterSet):
    """
    Фільтри для студентів:
    - branch  — за ID філії
    - status  — за статусом (active / archived)
    - group   — за ID групи (через M2M зв'язок Group.students)
    """
    group = django_filters.NumberFilter(
        field_name='groups',
        label='Група (ID)',
    )

    class Meta:
        model = Student
        fields = ['branch', 'status', 'group']
