from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .api_views import CustomUserViewSet
from .auth_views import PhoneLoginView, TokenRefreshView, LogoutView

router = SimpleRouter()
router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', PhoneLoginView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='token_logout'),
]
