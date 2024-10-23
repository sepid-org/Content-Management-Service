from django.db import models
from polymorphic.models import PolymorphicModel
from abc import abstractmethod

from apps.attributes.models.utils import SumDict
from proxies.bank_service.bank import request_transfer
from proxies.website_service.main import get_website


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

    def is_permitted(self, player):
        is_permitted = True

        for attribute in self.attributes.all():
            from .intrinsic_attributes import Condition

            if isinstance(attribute, Condition):
                is_permitted &= attribute.is_true(player)

        return is_permitted

    def give_reward(self, request):
        total_reward = SumDict({})

        for attribute in self.attributes.all():
            from .intrinsic_attributes import Reward
            if isinstance(attribute, Reward):
                total_reward += SumDict(attribute.value)

        if total_reward.is_zero():
            return

        # Get website
        website_name = request.headers.get('Website')
        website = get_website(website_name)

        # Process the transfer
        request_transfer(
            sender_id=website.get('uuid'),
            receiver_id=request.user.id,
            funds=total_reward,
        )

    @abstractmethod
    def perform(self, *args, **kwargs):
        pass

    class Meta:
        verbose_name = 'Performable Action'
        verbose_name_plural = 'Performable Actions'
