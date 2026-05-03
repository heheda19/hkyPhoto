from rest_framework import serializers
from .models import Album


class AlbumListSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['id', 'name', 'description', 'cover_url', 'photo_count', 'sort_order', 'created_at', 'updated_at']

    def get_cover_url(self, obj):
        if obj.cover:
            return obj.cover.thumbnail_url
        first = obj.photos.first()
        return first.thumbnail_url if first else None


class AlbumDetailSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'name', 'description', 'photo_count', 'sort_order', 'created_at', 'updated_at']


class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['name', 'description', 'sort_order']
