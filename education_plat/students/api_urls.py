from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),
]
