from rest_framework import serializers

from .models import Branch, Subject, Lesson


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

        # При PATCH branches може не передаватися — беремо поточні
        if branches is None and self.instance:
            branches = list(self.instance.branches.all())

        if name and branches:
            existing = Subject.objects.filter(
                name__iexact=name,
                branches__in=branches,
                status=Subject.Status.ACTIVE,
            )
            # Виключаємо поточний об'єкт при оновленні
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
