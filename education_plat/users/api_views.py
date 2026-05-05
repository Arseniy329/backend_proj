from rest_framework import viewsets

from .models import CustomUser
from .serializers import CustomUserSerializer, CustomUserCreateSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD-операцій з користувачами (адміни та викладачі).

    - GET    /api/users/          — список користувачів
    - POST   /api/users/          — створити нового користувача
    - GET    /api/users/{id}/     — деталі користувача
    - PUT    /api/users/{id}/     — повне оновлення
    - PATCH  /api/users/{id}/     — часткове оновлення
    - DELETE /api/users/{id}/     — видалити користувача
    """

    queryset = CustomUser.objects.all().order_by('-date_joined')
    search_fields = ['phone', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']

    def get_serializer_class(self):
        """
        При створенні використовуємо серіалізатор з полем password.
        В інших випадках — звичайний серіалізатор.
        """
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer
