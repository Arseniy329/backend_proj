from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для адміністративних та викладацьких акаунтів.
    Ідентифікація за номером телефону (не email).
    """

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'phone',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'phone': {
                'help_text': 'Унікальний номер телефону — основний ідентифікатор користувача.',
            },
        }

    def validate_phone(self, value):
        """
        Перевірка унікальності телефону з виключенням поточного об'єкта.
        """
        qs = CustomUser.objects.filter(phone=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Користувач з таким номером телефону вже існує.'
            )
        return value


class CustomUserCreateSerializer(CustomUserSerializer):
    """
    Серіалізатор для створення користувача (з паролем).
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ['password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
