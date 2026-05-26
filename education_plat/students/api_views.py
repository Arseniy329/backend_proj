from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Student
from .serializers import StudentSerializer
from .filters import StudentFilter


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій зі студентами (Student).

    - GET    /api/students/              — список студентів (з фільтрацією та пошуком)
    - POST   /api/students/              — створити нового студента
    - GET    /api/students/{id}/         — деталі студента
    - PUT    /api/students/{id}/         — повне оновлення
    - PATCH  /api/students/{id}/         — часткове оновлення
    - DELETE /api/students/{id}/         — м'яке видалення (архівування)
    - POST   /api/students/{id}/restore/ — відновлення з архіву

    Фільтрація (query params):
    - ?branch=1          — за філією
    - ?status=active     — за статусом
    - ?group=3           — за групою
    - ?search=Іван       — пошук за ім'ям або прізвищем
    """

    serializer_class = StudentSerializer
    filterset_class = StudentFilter
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        """
        Для адмінів повертає всіх студентів.
        Для решти — тільки активних.
        """
        qs = Student.objects.select_related(
            'branch',
        ).prefetch_related(
            'groups',
        ).order_by('-created_at')

        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs

        return qs.filter(status=Student.Status.ACTIVE)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete (архівування) замість фізичного видалення.

        Заплановані заняття, в яких бере участь студент,
        залишаються без змін у базі даних за правилами системи.
        """
        student = self.get_object()
        student.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Відновлення студента з архіву.
        POST /api/students/{id}/restore/
        """
        student = self.get_object()

        if not student.is_archived:
            return Response(
                {'error': 'Цей студент не є архівованим.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student.restore()
        serializer = self.get_serializer(student)
        return Response(serializer.data)
