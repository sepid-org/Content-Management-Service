from django.db import models
from polymorphic.models import PolymorphicModel


class Attribute(PolymorphicModel):
    name = models.CharField(max_length=50, unique=True)
    attributes = models.ManyToManyField(to='attributes.Attribute', blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class IntrinsicAttributeTypes(models.TextChoices):
    cost = 'cost'
    reward = 'reward'
    required_balance = 'required_balance'
    password = 'password'
    disabled = 'disabled'


class IntrinsicAttribute(Attribute):
    value = models.JSONField(default=dict, null=True, blank=True)
    type = models.CharField(
        max_length=20, choices=IntrinsicAttributeTypes.choices)


class PerformableActionTypes(models.TextChoices):
    see = 'see'
    purchase = 'purchase'
    sell = 'sell'
    copy = 'copy'
    solve = 'solve'
    attempt = 'attempt'
    enter = 'enter'
    transit = 'transit'


class PerformableAction(Attribute):
    type = models.CharField(
        max_length=20, choices=PerformableActionTypes.choices)
