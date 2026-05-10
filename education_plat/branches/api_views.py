from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Branch, Subject, Lesson, Group, SubscriptionPlan, Attendance
from .permissions import (
    IsAdminRole,
    IsAdminOrTeacherOwnLesson,
    IsAdminOrTeacherMarkAttendance,
)
from .serializers import (
    BranchSerializer,
    SubjectSerializer,
    GroupSerializer,
    SubscriptionPlanSerializer,
    LessonSerializer,
    AttendanceSerializer,
)
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
    permission_classes = [IsAdminRole]

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
    permission_classes = [IsAdminRole]

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


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій з групами (Group).

    - GET    /api/groups/              — список груп (з фільтрацією)
    - POST   /api/groups/              — створити нову групу
    - GET    /api/groups/{id}/         — деталі групи
    - PUT    /api/groups/{id}/         — повне оновлення
    - PATCH  /api/groups/{id}/         — часткове оновлення
    - DELETE /api/groups/{id}/         — деактивація групи (status → inactive)

    Фільтрація (query params):
    - ?branch=1          — за філією
    - ?status=active     — за статусом
    - ?search=Група      — пошук за назвою
    """

    serializer_class = GroupSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ['branch', 'status']
    search_fields = ['name']

    def get_queryset(self):
        """
        ADMIN — всі групи.
        TEACHER — лише групи, в яких є заняття цього викладача.
        """
        qs = Group.objects.select_related('branch').prefetch_related(
            'subjects', 'students',
        ).order_by('-created_at')

        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return qs

        if user.is_authenticated and user.is_teacher:
            return qs.filter(
                status=Group.Status.ACTIVE,
                lessons__teacher=user,
            ).distinct()

        return qs.filter(status=Group.Status.ACTIVE)

    def destroy(self, request, *args, **kwargs):
        """
        Деактивація групи замість фізичного видалення.

        Перед деактивацією перевіряє, чи є заплановані заняття
        в цій групі. Якщо є — повертає HTTP 400.
        """
        group = self.get_object()

        scheduled_lessons_count = Lesson.objects.filter(
            group=group,
            status=Lesson.Status.SCHEDULED,
        ).count()

        if scheduled_lessons_count > 0:
            return Response(
                {
                    'error': (
                        f'Неможливо деактивувати групу "{group.name}": '
                        f'є {scheduled_lessons_count} запланованих занять. '
                        f'Спочатку скасуйте або завершіть їх.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        group.status = Group.Status.INACTIVE
        group.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Повторна активація групи.
        POST /api/groups/{id}/activate/
        """
        group = self.get_object()

        if group.status == Group.Status.ACTIVE:
            return Response(
                {'error': 'Ця група вже активна.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group.status = Group.Status.ACTIVE
        group.save(update_fields=['status'])
        serializer = self.get_serializer(group)
        return Response(serializer.data)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій з абонементами (SubscriptionPlan).

    - GET    /api/subscription-plans/          — список абонементів
    - POST   /api/subscription-plans/          — створити новий абонемент
    - GET    /api/subscription-plans/{id}/     — деталі абонемента
    - PUT    /api/subscription-plans/{id}/     — повне оновлення
    - PATCH  /api/subscription-plans/{id}/     — часткове оновлення
    - DELETE /api/subscription-plans/{id}/     — видалити абонемент

    Фільтрація (query params):
    - ?branch=1          — за філією
    """

    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ['branch']
    search_fields = ['name']

    def get_queryset(self):
        """
        ADMIN — всі абонементи.
        TEACHER — лише абонементи філій, де він має заняття.
        """
        qs = SubscriptionPlan.objects.select_related(
            'branch',
        ).order_by('-created_at')

        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return qs

        if user.is_authenticated and user.is_teacher:
            teacher_branch_ids = Lesson.objects.filter(
                teacher=user,
            ).values_list('group__branch_id', flat=True).distinct()
            return qs.filter(branch_id__in=teacher_branch_ids)

        return qs


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій із заняттями (Lesson).

    - GET    /api/lessons/                          — список занять (з фільтрацією)
    - POST   /api/lessons/                          — створити нове заняття
    - GET    /api/lessons/{id}/                     — деталі заняття
    - PUT    /api/lessons/{id}/                     — повне оновлення
    - PATCH  /api/lessons/{id}/                     — часткове оновлення
    - DELETE /api/lessons/{id}/                     — скасувати заняття (status → cancelled)
    - POST   /api/lessons/{id}/complete/            — завершити заняття (status → completed)
    - POST   /api/lessons/{id}/mark_attendance/     — масова відмітка відвідуваності

    Фільтрація (query params):
    - ?group=1           — за групою
    - ?teacher=2         — за викладачем
    - ?status=scheduled  — за статусом
    - ?date=2026-05-10   — за датою
    - ?search=тема       — пошук за темою
    """

    serializer_class = LessonSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ['group', 'teacher', 'status', 'date']
    search_fields = ['topic']

    def get_queryset(self):
        """
        ADMIN — всі заняття.
        TEACHER — лише заняття, де він є викладачем.
        """
        qs = Lesson.objects.select_related(
            'group', 'group__branch', 'subject', 'teacher',
        ).order_by('date', 'start_time')

        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return qs

        if user.is_authenticated and user.is_teacher:
            return qs.filter(teacher=user)

        return qs

    def destroy(self, request, *args, **kwargs):
        """
        Скасування заняття замість фізичного видалення.
        Лише заплановане (scheduled) заняття можна скасувати.
        """
        lesson = self.get_object()

        if lesson.status != Lesson.Status.SCHEDULED:
            return Response(
                {
                    'error': (
                        f'Неможливо скасувати заняття зі статусом '
                        f'"{lesson.get_status_display()}". '
                        f'Скасовувати можна лише заплановані заняття.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson.status = Lesson.Status.CANCELLED
        lesson.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Завершення заняття.
        POST /api/lessons/{id}/complete/

        Лише заплановане (scheduled) заняття можна завершити.
        """
        lesson = self.get_object()

        if lesson.status != Lesson.Status.SCHEDULED:
            return Response(
                {
                    'error': (
                        f'Неможливо завершити заняття зі статусом '
                        f'"{lesson.get_status_display()}". '
                        f'Завершувати можна лише заплановані заняття.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson.status = Lesson.Status.COMPLETED
        lesson.save(update_fields=['status'])
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminOrTeacherMarkAttendance],
    )
    def mark_attendance(self, request, pk=None):
        """
        Масова відмітка відвідуваності для заняття.
        POST /api/lessons/{id}/mark_attendance/

        Body:
        {
            "records": [
                {"student": 1, "status": "present", "note": ""},
                {"student": 2, "status": "absent", "note": "хвороба"}
            ]
        }

        Створює або оновлює записи відвідуваності для вказаних студентів.
        Викладач може відмічати лише на своїх заняттях.
        """
        lesson = self.get_object()
        self.check_object_permissions(request, lesson)

        if lesson.status == Lesson.Status.CANCELLED:
            return Response(
                {'error': 'Неможливо відмітити відвідуваність для скасованого заняття.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records = request.data.get('records', [])
        if not records:
            return Response(
                {'error': 'Поле "records" є обов\'язковим і не може бути порожнім.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group_student_ids = set(
            lesson.group.students.values_list('id', flat=True)
        )

        created = []
        updated = []
        errors = []

        for i, record in enumerate(records):
            student_id = record.get('student')
            att_status = record.get('status', Attendance.Status.PRESENT)
            note = record.get('note', '')

            if student_id not in group_student_ids:
                errors.append({
                    'index': i,
                    'student': student_id,
                    'error': f'Студент ID={student_id} не належить до групи "{lesson.group.name}".',
                })
                continue

            if att_status not in dict(Attendance.Status.choices):
                errors.append({
                    'index': i,
                    'student': student_id,
                    'error': f'Невалідний статус "{att_status}".',
                })
                continue

            attendance, is_new = Attendance.objects.update_or_create(
                lesson=lesson,
                student_id=student_id,
                defaults={
                    'status': att_status,
                    'note': note,
                },
            )

            serialized = AttendanceSerializer(attendance).data
            if is_new:
                created.append(serialized)
            else:
                updated.append(serialized)

        return Response(
            {
                'created': created,
                'updated': updated,
                'errors': errors,
            },
            status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS
            if created or updated else status.HTTP_400_BAD_REQUEST,
        )


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій з відвідуваністю (Attendance).

    - GET    /api/attendances/              — список записів відвідуваності
    - POST   /api/attendances/              — створити запис
    - GET    /api/attendances/{id}/         — деталі запису
    - PUT    /api/attendances/{id}/         — повне оновлення
    - PATCH  /api/attendances/{id}/         — часткове оновлення (напр. зміна статусу)
    - DELETE /api/attendances/{id}/         — видалити запис

    Фільтрація (query params):
    - ?lesson=1          — за заняттям
    - ?student=2         — за студентом
    - ?status=present    — за статусом
    """

    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacherOwnLesson]
    filterset_fields = ['lesson', 'student', 'status']

    def get_queryset(self):
        """
        ADMIN — всі записи відвідуваності.
        TEACHER — лише відвідуваність на своїх заняттях.
        """
        qs = Attendance.objects.select_related(
            'lesson', 'lesson__group', 'student',
        ).order_by('-created_at')

        user = self.request.user
        if user.is_authenticated and user.is_admin:
            return qs

        if user.is_authenticated and user.is_teacher:
            return qs.filter(lesson__teacher=user)

        return qs
