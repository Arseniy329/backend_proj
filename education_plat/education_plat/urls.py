from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('branches.urls')),
    path('', include('students.urls')),

    # API
    path('api/', include('branches.api_urls')),
    path('api/', include('users.api_urls')),
    path('api/', include('students.api_urls')),

    # API Documentation (Swagger / OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
