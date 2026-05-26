from rest_framework import serializers

from .models import Branch, Subject, Lesson, Group, SubscriptionPlan, Attendance
from .validators import check_schedule_conflicts, get_group_student_ids
from students.models import Student


class BranchSerializer(serializers.ModelSerializer):
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id',
            'name',
            'address',
            'city',
            'status',
            'is_archived',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.filter(status=Branch.Status.ACTIVE),
        required=True,
    )

    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'description',
            'status',
            'branch',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, attrs):
        """
        Перевірка унікальності назви предмета в межах філії.
        """
        name = attrs.get('name', getattr(self.instance, 'name', None))
        branch = attrs.get('branch', getattr(self.instance, 'branch', None))
        if name and branch:
            existing = Subject.objects.filter(
                name__iexact=name,
                branch=branch,
                status=Subject.Status.ACTIVE,
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    'name': (
                        f'Предмет з назвою "{name}" вже існує у філії "{branch}".'
                    ),
                })
        return attrs


class GroupSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для груп.

    M2M-зв'язки (subjects, students) передаються як списки ID.
    Валідація:
    - Назва групи унікальна в межах однієї філії (серед активних груп).
    - Філія повинна бути активною.
    """
    subjects = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Subject.objects.filter(status=Subject.Status.ACTIVE),
        required=False,
    )
    students = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Student.objects.filter(status=Student.Status.ACTIVE),
        required=False,
    )

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'branch',
            'subjects',
            'students',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_branch(self, value):
        """
        Забороняє прикріплення групи до архівованої філії.
        """
        if value.status == Branch.Status.ARCHIVED:
            raise serializers.ValidationError(
                f'Філія "{value.name}" архівована. '
                f'Неможливо створити групу в архівованій філії.'
            )
        return value

    def validate(self, attrs):
        """
        Перевірка унікальності назви групи в межах філії
        (лише серед активних груп).
        """
        name = attrs.get('name', getattr(self.instance, 'name', None))
        branch = attrs.get('branch', getattr(self.instance, 'branch', None))

        if name and branch:
            existing = Group.objects.filter(
                name__iexact=name,
                branch=branch,
                status=Group.Status.ACTIVE,
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError({
                    'name': (
                        f'Група з назвою "{name}" вже існує '
                        f'у філії "{branch.name}".'
                    ),
                })

        return attrs


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для абонементних планів.

    Валідація:
    - Ціна > 0.
    - Кількість занять > 0.
    - Тривалість > 0 днів.
    - Філія повинна бути активною.
    """

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'lessons_count',
            'price',
            'duration_days',
            'branch',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_branch(self, value):
        """
        Забороняє створення абонемента для архівованої філії.
        """
        if value.status == Branch.Status.ARCHIVED:
            raise serializers.ValidationError(
                f'Філія "{value.name}" архівована. '
                f'Неможливо створити абонемент для архівованої філії.'
            )
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Ціна повинна бути більше нуля.'
            )
        return value

    def validate_lessons_count(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Кількість занять повинна бути більше нуля.'
            )
        return value

    def validate_duration_days(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Тривалість повинна бути більше нуля днів.'
            )
        return value


class LessonSerializer(serializers.ModelSerializer):


    class Meta:
        model = Lesson
        fields = [
            'id',
            'group',
            'subject',
            'teacher',
            'date',
            'start_time',
            'end_time',
            'topic',
            'room',
            'notes',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_subject(self, value):
        """
        Забороняє створення/оновлення заняття з архівованим предметом.
        """
        if value and value.status == Subject.Status.ARCHIVED:
            raise serializers.ValidationError(
                f'Предмет "{value.name}" архівовано. '
                f'Неможливо створити заняття з архівованим предметом.'
            )
        return value

    def validate(self, attrs):

        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        date = attrs.get('date', getattr(self.instance, 'date', None))
        teacher = attrs.get('teacher', getattr(self.instance, 'teacher', None))
        group = attrs.get('group', getattr(self.instance, 'group', None))

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'end_time': (
                    f'Час закінчення ({end_time}) повинен бути '
                    f'строго пізніше часу початку ({start_time}).'
                ),
            })

        if date and start_time and end_time:
            exclude_id = self.instance.pk if self.instance else None
            student_ids = get_group_student_ids(group) if group else None

            conflicts = check_schedule_conflicts(
                date=date,
                start_time=start_time,
                end_time=end_time,
                teacher=teacher,
                student_ids=student_ids,
                exclude_lesson_id=exclude_id,
            )

            if conflicts:
                error_messages = [c['message'] for c in conflicts]
                raise serializers.ValidationError({
                    'schedule_conflict': error_messages,
                })

        return attrs


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для відвідуваності.

    Валідація:
    - Студент повинен належати до групи заняття.
    - Пара (lesson, student) унікальна (unique_together).
    - Заняття не повинно бути скасоване.
    """

    class Meta:
        model = Attendance
        fields = [
            'id',
            'lesson',
            'student',
            'status',
            'note',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        """
        1. Перевірка: студент належить до групи заняття.
        2. Перевірка: дублікат (lesson + student) — тільки при створенні.
        3. Перевірка: заняття не скасоване.
        """
        lesson = attrs.get('lesson', getattr(self.instance, 'lesson', None))
        student = attrs.get('student', getattr(self.instance, 'student', None))

        if lesson and lesson.status == Lesson.Status.CANCELLED:
            raise serializers.ValidationError({
                'lesson': 'Неможливо відмітити відвідуваність для скасованого заняття.',
            })

        if lesson and student:
            group_student_ids = lesson.group.students.values_list('id', flat=True)
            if student.pk not in group_student_ids:
                raise serializers.ValidationError({
                    'student': (
                        f'Студент "{student}" не належить до групи '
                        f'"{lesson.group.name}".'
                    ),
                })

            # Перевірка unique_together тільки при створенні
            if not self.instance:
                if Attendance.objects.filter(
                    lesson=lesson,
                    student=student,
                ).exists():
                    raise serializers.ValidationError({
                        'non_field_errors': (
                            f'Відвідуваність для студента "{student}" '
                            f'на занятті "{lesson}" вже зафіксована.'
                        ),
                    })

        return attrs

