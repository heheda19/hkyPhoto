from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_ext.urls')),
    path('api/', include('albums.urls')),
    path('api/', include('photos.urls')),
    path('api/', include('locations.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
    re_path(r'^(?!api/|admin/|static/).*$', TemplateView.as_view(template_name='index.html')),
]
