from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Location
from .serializers import LocationListSerializer, LocationDetailSerializer
from photos.serializers import PhotoListSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationListSerializer
        return LocationDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return sorted(qs, key=lambda loc: loc.photo_count, reverse=True)

    @action(detail=True, methods=['get'])
    def photos(self, request, id=None):
        location = self.get_object()
        photos = location.photos.all().order_by('-taken_at', '-uploaded_at')
        page = self.paginate_queryset(photos)
        if page is not None:
            return self.get_paginated_response(PhotoListSerializer(page, many=True).data)
        return Response(PhotoListSerializer(photos, many=True).data)
