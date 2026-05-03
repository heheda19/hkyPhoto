from django.contrib import admin
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'taken_at', 'uploaded_at']
    list_filter = ['album', 'location']
    search_fields = ['title']
