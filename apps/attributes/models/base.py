from django.db import models
from polymorphic.models import PolymorphicModel
from abc import abstractmethod


class Attribute(PolymorphicModel):
    """Base model for all attributes."""
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    attributes = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='related_to')

    def __str__(self):
        return self.title


class IntrinsicAttribute(Attribute):
    """Attributes that have intrinsic values."""
    value = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = 'Intrinsic Attribute'
        verbose_name_plural = 'Intrinsic Attributes'


class PerformableAction(Attribute):
    """Attributes representing actions that can be performed."""

    @abstractmethod
    def perform(self, *args, **kwargs):
        pass

    class Meta:
        verbose_name = 'Performable Action'
        verbose_name_plural = 'Performable Actions'
