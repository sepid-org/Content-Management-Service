from django.db import models
from polymorphic.models import PolymorphicModel

from apps.attributes.models.utils import SumDict
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

    def is_permitted(self, *args, **kwargs) -> bool:
        is_permitted = True

        from .intrinsic_attributes import Condition
        condition_attributes = self.attributes.instance_of(Condition)
        for condition in condition_attributes:
            is_permitted &= condition.is_true(*args, **kwargs)

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

    def give_reward(self, *args, **kwargs):
        total_reward = SumDict({})

        from .intrinsic_attributes import Reward
        reward_attributes = self.attributes.instance_of(Reward)
        for reward in reward_attributes:
            total_reward += SumDict(reward.value)

        if total_reward.is_zero():
            return

        # Process the transfer
        request = kwargs.get('request')
        website_name = request.headers.get('Website')
        transfer_funds_to_user(
            website_name=website_name,
            user_uuid=str(request.user.id),
            funds=total_reward,
        )

    def perform(self, *args, **kwargs) -> bool:
        if not self.is_permitted(*args, **kwargs):
            return False
        return True

    class Meta:
        verbose_name = 'Performable Action'
        verbose_name_plural = 'Performable Actions'
