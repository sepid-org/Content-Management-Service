from django.db import models

from apps.fsm.models.base import Paper


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Article(Paper):
    website = models.CharField(blank=True, null=True, max_length=50)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_image = models.URLField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
