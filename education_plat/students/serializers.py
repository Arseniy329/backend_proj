from rest_framework import serializers

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для студентів з усіма обов'язковими полями профілю:
    персональні дані, контактна інформація, дані батьків/опікунів,
    прикріплена філія, статус.
    """
    is_archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone',
            'date_of_birth',
            'parent_name',
            'parent_phone',
            'parent_email',
            'branch',
            'status',
            'is_archived',
            'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at']
