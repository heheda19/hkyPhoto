from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Album
from .serializers import AlbumListSerializer, AlbumDetailSerializer, AlbumCreateSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return AlbumListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return AlbumCreateSerializer
        return AlbumDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'])
    def photos(self, request, id=None):
        album = self.get_object()
        from photos.serializers import PhotoListSerializer
        photos = album.photos.all().order_by('-taken_at', '-uploaded_at')
        page = self.paginate_queryset(photos)
        if page is not None:
            return self.get_paginated_response(PhotoListSerializer(page, many=True).data)
        return Response(PhotoListSerializer(photos, many=True).data)
