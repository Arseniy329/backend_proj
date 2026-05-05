from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('branches.urls')),
    path('', include('students.urls')),

    # API
    path('api/', include('branches.api_urls')),
    path('api/', include('users.api_urls')),
    path('api/', include('students.api_urls')),
]
