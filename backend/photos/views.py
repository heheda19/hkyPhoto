import uuid
from datetime import datetime
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Photo
from .serializers import PhotoListSerializer, PhotoCreateSerializer, PresignedUrlSerializer
from .utils import get_oss_bucket


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().select_related('album', 'location')
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ('create',):
            return PhotoCreateSerializer
        return PhotoListSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy', 'presigned_url'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        album_id = request.query_params.get('album_id')
        location_id = request.query_params.get('location_id')
        if album_id:
            queryset = queryset.filter(album_id=album_id)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        ordering = request.query_params.get('ordering', '-taken_at')
        allowed_orderings = {'taken_at', '-taken_at', 'uploaded_at', '-uploaded_at', 'file_size', '-file_size'}
        if ordering not in allowed_orderings:
            ordering = '-taken_at'
        queryset = queryset.order_by(ordering)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(PhotoListSerializer(page, many=True).data)
        return Response(PhotoListSerializer(queryset, many=True).data)

    @action(detail=False, methods=['post'])
    def presigned_url(self, request):
        serializer = PresignedUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content_type = serializer.validated_data['content_type']
        allowed_cts = {'image/jpeg', 'image/png', 'image/heic', 'image/heif', 'image/webp', 'image/tiff'}
        if content_type not in allowed_cts:
            content_type = 'image/jpeg'
        filename = serializer.validated_data['filename']
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
        oss_key = f"photos/{datetime.now().strftime('%Y/%m')}/{uuid.uuid4().hex}.{ext}"
        bucket = get_oss_bucket()
        url = bucket.sign_url('PUT', oss_key, 300, headers={'Content-Type': content_type})
        return Response({'oss_key': oss_key, 'upload_url': url})

    def perform_create(self, serializer):
        photo = serializer.save()
        if photo.latitude and photo.longitude:
            self._assign_location(photo)

    def _assign_location(self, photo):
        import requests
        from locations.models import Location
        try:
            resp = requests.get('https://restapi.amap.com/v3/geocode/regeo', params={
                'key': settings.AMAP_API_KEY,
                'location': f'{photo.longitude},{photo.latitude}',
                'extensions': 'base',
            }, timeout=5)
            data = resp.json()
            if data['status'] == '1' and data['regeocode']:
                addr = data['regeocode']['addressComponent']
                city = addr.get('city', '') or addr.get('province', '')
                province = addr.get('province', '')
                country = addr.get('country', '')
                name_parts = [country, province, city]
                name = ''.join(p for p in name_parts if p) or '未知地点'

                location, _ = Location.objects.get_or_create(
                    name=name,
                    defaults={
                        'latitude': photo.latitude,
                        'longitude': photo.longitude,
                        'city': city,
                        'province': province,
                        'country': country,
                    }
                )
                photo.location = location
                photo.save(update_fields=['location'])
        except (requests.RequestException, ValueError, KeyError):
            pass
