from rest_framework import serializers
from .models import Location


class LocationListSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'province', 'country', 'photo_count', 'cover_url']

    def get_cover_url(self, obj):
        first = obj.photos.first()
        return first.thumbnail_url if first else None


class LocationDetailSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'province', 'country', 'photo_count', 'latitude', 'longitude']
