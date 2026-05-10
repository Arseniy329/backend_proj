from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    BranchViewSet,
    SubjectViewSet,
    GroupViewSet,
    SubscriptionPlanViewSet,
    LessonViewSet,
    AttendanceViewSet,
)

router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscriptionplan')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'attendances', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]

