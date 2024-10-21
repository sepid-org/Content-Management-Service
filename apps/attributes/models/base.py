from django.db import models
from polymorphic.models import PolymorphicModel
from abc import abstractmethod


class Attribute(PolymorphicModel):
    """Base model for all attributes."""
    name = models.CharField(max_length=50, unique=True)
    attributes = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='related_to')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class IntrinsicAttributeTypes(models.TextChoices):
    """Enumeration for intrinsic attribute types."""
    COST = 'cost', 'Cost'
    REWARD = 'reward', 'Reward'
    REQUIRED_BALANCE = 'required_balance', 'Required Balance'
    PASSWORD = 'password', 'Password'
    DISABLED = 'disabled', 'Disabled'
    CONDITION = 'condition', 'Condition'


class IntrinsicAttribute(Attribute):
    """Attributes that have intrinsic values."""
    value = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = 'Intrinsic Attribute'
        verbose_name_plural = 'Intrinsic Attributes'


class PerformableActionTypes(models.TextChoices):
    """Enumeration for performable actions."""
    SEE = 'see', 'See'
    PURCHASE = 'purchase', 'Purchase'
    SELL = 'sell', 'Sell'
    COPY = 'copy', 'Copy'
    ASSESS_ANSWER = 'assess_answer', 'Assess Answer'
    SOLVE = 'solve', 'Solve'
    SUBMIT = 'submit', 'Submit'
    ENTER = 'enter', 'Enter'
    TRANSIT = 'transit', 'Transit'


class PerformableAction(Attribute):
    """Attributes representing actions that can be performed."""

    @abstractmethod
    def perform(self, *args, **kwargs):
        pass

    class Meta:
        verbose_name = 'Performable Action'
        verbose_name_plural = 'Performable Actions'
