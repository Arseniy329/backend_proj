from rest_framework import serializers

from .models import Branch, Subject, Lesson, Group
from .validators import check_schedule_conflicts, get_group_student_ids


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
    branches = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Branch.objects.filter(status=Branch.Status.ACTIVE),
        required=False,
    )

    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'description',
            'status',
            'branches',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, attrs):
        """
        Перевірка унікальності назви предмета в межах кожної філії.

        Subject ↔ Branch — це M2M, тому UniqueTogetherValidator
        не підходить. Перевіряємо вручну: для кожної обраної філії
        не повинно існувати іншого активного предмета з такою ж назвою.
        """
        name = attrs.get('name', getattr(self.instance, 'name', None))
        branches = attrs.get('branches', None)

        if branches is None and self.instance:
            branches = list(self.instance.branches.all())

        if name and branches:
            existing = Subject.objects.filter(
                name__iexact=name,
                branches__in=branches,
                status=Subject.Status.ACTIVE,
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                conflicting = existing.first()
                raise serializers.ValidationError({
                    'name': (
                        f'Предмет з назвою "{name}" вже існує '
                        f'у філії "{conflicting.branches.first()}".'
                    ),
                })

        return attrs


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

