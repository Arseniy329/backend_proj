from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import BranchViewSet, SubjectViewSet

router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'subjects', SubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]
