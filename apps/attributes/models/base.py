from django.db import models
from polymorphic.models import PolymorphicModel

from apps.attributes.models.utils import get_object_net_rewards
from proxies.bank_service.utils import transfer_funds_to_user


class Attribute(PolymorphicModel):
    """Base model for all attributes."""
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    attributes = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='related_to',
    )

    def is_permitted(self, user, player=None) -> bool:
        is_permitted = True

        from .intrinsic_attributes import Condition
        condition_attributes = self.attributes.instance_of(Condition)
        for condition in condition_attributes:
            is_permitted &= condition.is_true(user, player)

        return is_permitted

    def get_related_attributes(self):
        # Returns a comma-separated string of related attribute titles
        return ", ".join([attr.title for attr in self.attributes.all()])

    get_related_attributes.short_description = "Related Attributes"

    def __str__(self):
        return f'{self.__class__.__name__}: {self.title}'


class IntrinsicAttribute(Attribute):
    """Attributes that have intrinsic values."""
    value = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = 'Intrinsic Attribute'
        verbose_name_plural = 'Intrinsic Attributes'


class PerformableAction(Attribute):
    """Attributes representing actions that can be performed."""

    def give_reward(self, user, player, website):
        net_rewards = get_object_net_rewards(self)

        if net_rewards.is_zero():
            return

        # Process the transfer
        transfer_funds_to_user(
            # todo:
            # website_uuid=website.get('uuid'),
            website_uuid=website,
            user_uuid=str(user.id),
            funds=net_rewards,
        )

    def perform(self, user, player, website) -> bool:
        if not self.is_permitted(user, player):
            return False
        return True

    class Meta:
        verbose_name = 'Performable Action'
        verbose_name_plural = 'Performable Actions'
