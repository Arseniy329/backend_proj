from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .api_views import StudentViewSet

router = SimpleRouter()
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]
