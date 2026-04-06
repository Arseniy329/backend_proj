from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/archive/', views.student_archive, name='student_archive'),
    path('students/<int:pk>/restore/', views.student_restore, name='student_restore'),
]
