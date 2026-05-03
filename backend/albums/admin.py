from django.contrib import admin
from .models import Album


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'created_at']
    search_fields = ['name']
