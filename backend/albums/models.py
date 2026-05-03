import uuid
from django.db import models


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    cover = models.ForeignKey('photos.Photo', on_delete=models.SET_NULL, null=True, blank=True, related_name='cover_of')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name

    @property
    def photo_count(self):
        return self.photos.count()
