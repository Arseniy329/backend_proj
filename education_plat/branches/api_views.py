from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Branch, Subject, Lesson
from .serializers import BranchSerializer, SubjectSerializer
from students.models import Student


class BranchViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій з філіями (Branch).

    - GET    /api/branches/          — список активних філій (адміни бачать усі)
    - POST   /api/branches/          — створити нову філію
    - GET    /api/branches/{id}/     — деталі філії
    - PUT    /api/branches/{id}/     — повне оновлення
    - PATCH  /api/branches/{id}/     — часткове оновлення
    - DELETE /api/branches/{id}/     — м'яке видалення (архівування)
    - POST   /api/branches/{id}/restore/ — відновлення з архіву
    """

    serializer_class = BranchSerializer

    def get_queryset(self):
        """
        Для адмінів повертає всі філії.
        Для решти — тільки активні (не архівовані).
        """
        qs = Branch.objects.all().order_by('-created_at')

        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs

        return qs.filter(status=Branch.Status.ACTIVE)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete (архівування) замість фізичного видалення.

        Перед архівуванням перевіряє:
        1. Чи є активні студенти, прикріплені до цієї філії.
        2. Чи є заплановані (scheduled) заняття у групах цієї філії.

        Якщо є — повертає HTTP 400 з описом проблеми.
        """
        branch = self.get_object()

        # Перевірка: активні студенти
        active_students_count = Student.objects.filter(
            branch=branch,
            status=Student.Status.ACTIVE,
        ).count()

        if active_students_count > 0:
            return Response(
                {
                    'error': (
                        f'Неможливо архівувати філію "{branch.name}": '
                        f'є {active_students_count} активних студентів. '
                        f'Спочатку перемістіть або архівуйте їх.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Перевірка: заплановані заняття
        scheduled_lessons_count = Lesson.objects.filter(
            group__branch=branch,
            status=Lesson.Status.SCHEDULED,
        ).count()

        if scheduled_lessons_count > 0:
            return Response(
                {
                    'error': (
                        f'Неможливо архівувати філію "{branch.name}": '
                        f'є {scheduled_lessons_count} запланованих занять. '
                        f'Спочатку скасуйте або завершіть їх.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Якщо залежностей немає — архівуємо
        branch.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Відновлення філії з архіву.
        POST /api/branches/{id}/restore/
        """
        branch = self.get_object()

        if not branch.is_archived:
            return Response(
                {'error': 'Ця філія не є архівованою.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        branch.restore()
        serializer = self.get_serializer(branch)
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій з предметами (Subject).

    - GET    /api/subjects/              — список активних предметів
    - POST   /api/subjects/              — створити новий предмет
    - GET    /api/subjects/{id}/         — деталі предмета
    - PUT    /api/subjects/{id}/         — повне оновлення
    - PATCH  /api/subjects/{id}/         — часткове оновлення
    - DELETE /api/subjects/{id}/         — м'яке видалення (архівування)
    - POST   /api/subjects/{id}/restore/ — відновлення з архіву
    """

    serializer_class = SubjectSerializer

    def get_queryset(self):
        """
        Для адмінів повертає всі предмети.
        Для решти — тільки активні.
        """
        qs = Subject.objects.all().order_by('-created_at')

        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs

        return qs.filter(status=Subject.Status.ACTIVE)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete (архівування) замість фізичного видалення.

        Перед архівуванням перевіряє, чи є заплановані заняття
        з цим предметом. Якщо є — повертає HTTP 400.
        """
        subject = self.get_object()

        scheduled_lessons_count = Lesson.objects.filter(
            subject=subject,
            status=Lesson.Status.SCHEDULED,
        ).count()

        if scheduled_lessons_count > 0:
            return Response(
                {
                    'error': (
                        f'Неможливо архівувати предмет "{subject.name}": '
                        f'є {scheduled_lessons_count} запланованих занять. '
                        f'Спочатку скасуйте або завершіть їх.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        subject.status = Subject.Status.ARCHIVED
        subject.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Відновлення предмета з архіву.
        POST /api/subjects/{id}/restore/
        """
        subject = self.get_object()

        if subject.status != Subject.Status.ARCHIVED:
            return Response(
                {'error': 'Цей предмет не є архівованим.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subject.status = Subject.Status.ACTIVE
        subject.save(update_fields=['status'])
        serializer = self.get_serializer(subject)
        return Response(serializer.data)
