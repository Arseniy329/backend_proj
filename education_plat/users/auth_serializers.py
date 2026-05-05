from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class PhoneLoginSerializer(serializers.Serializer):

    phone = serializers.CharField(
        label='Номер телефону',
        help_text='Номер телефону у форматі +380XXXXXXXXX',
    )
    password = serializers.CharField(
        label='Пароль',
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=phone,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                {'detail': 'Невірний номер телефону або пароль.'},
                code='authorization',
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': 'Акаунт заблоковано. Зверніться до адміністратора.'},
                code='authorization',
            )

        attrs['user'] = user
        return attrs

    def get_tokens(self):
        """
        Генерує пару access + refresh токенів для автентифікованого користувача.
        """
        user = self.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class TokenRefreshResponseSerializer(serializers.Serializer):

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(
        read_only=True,
        help_text='Новий refresh-токен (старий більше не діє — одноразове використання).',
    )


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField(
        help_text='Refresh-токен, який потрібно анулювати.',
    )
