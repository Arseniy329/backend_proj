from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTRefreshView

from .auth_serializers import PhoneLoginSerializer, LogoutSerializer


class PhoneLoginView(APIView):
    """
    Вхід користувача за номером телефону та паролем.

    POST /api/auth/login/
    Body: { "phone": "+380991234567", "password": "secret" }

    Відповідь:
    {
        "access": "<access-token>",
        "refresh": "<refresh-token>",
        "user": { "id", "phone", "full_name", "role" }
    }

    Безпека:
    - Неактивні (архівовані) користувачі отримують зрозуміле повідомлення.
    - При невірних реквізитах — уніфікована помилка (не розкриваємо деталі).
    """

    permission_classes = [AllowAny]
    serializer_class = PhoneLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = PhoneLoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = serializer.get_tokens()

        return Response(
            {
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'id': user.pk,
                    'phone': user.phone,
                    'full_name': f'{user.first_name} {user.last_name}'.strip(),
                    'role': user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshView(SimpleJWTRefreshView):
    """
    Оновлення access-токена за допомогою refresh-токена.

    POST /api/auth/refresh/
    Body: { "refresh": "<refresh-token>" }

    Відповідь: { "access": "<новий-access>", "refresh": "<новий-refresh>" }

    Ротація:
    - Після кожного запиту старий refresh-токен анулюється (blacklist).
    - Видається новий refresh-токен (одноразове використання).
    - Налаштовується через SIMPLE_JWT: ROTATE_REFRESH_TOKENS=True,
      BLACKLIST_AFTER_ROTATION=True.
    """

    permission_classes = [AllowAny]


class LogoutView(APIView):
 
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError as e:
            raise InvalidToken({'detail': str(e)})

        return Response(
            {'detail': 'Успішно вийшли з системи.'},
            status=status.HTTP_200_OK,
        )
