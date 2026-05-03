from rest_framework import serializers
from .models import Photo


class PhotoListSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.URLField(read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, default=None)

    class Meta:
        model = Photo
        fields = ['id', 'album', 'title', 'thumbnail_url', 'width', 'height',
                  'taken_at', 'location_name', 'latitude', 'longitude', 'uploaded_at']


class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'album', 'title', 'oss_key', 'width', 'height',
                  'file_size', 'taken_at', 'latitude', 'longitude']


class PresignedUrlSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=500)
    content_type = serializers.CharField(default='image/jpeg')
