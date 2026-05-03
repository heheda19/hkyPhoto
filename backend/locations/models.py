import uuid
from django.db import models


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100, blank=True, default='')
    province = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['country', 'province', 'city']

    def __str__(self):
        return self.name

    @property
    def photo_count(self):
        return self.photos.count()
