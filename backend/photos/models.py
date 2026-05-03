import uuid
from django.db import models


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey('albums.Album', on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200, blank=True, default='')
    oss_key = models.CharField(max_length=500)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    taken_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at', '-uploaded_at']

    def __str__(self):
        return self.title or f'Photo {self.id}'

    @property
    def thumbnail_url(self):
        from .utils import get_thumbnail_url
        return get_thumbnail_url(self.oss_key, 400)

    @property
    def full_url(self):
        from .utils import generate_presigned_url
        return generate_presigned_url(self.oss_key, 3600)
