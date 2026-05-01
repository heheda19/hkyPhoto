from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_ext.urls')),
    path('api/', include('albums.urls')),
    path('api/', include('photos.urls')),
    path('api/', include('locations.urls')),
]
