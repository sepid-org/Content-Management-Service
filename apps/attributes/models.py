from django.db import models

# Create your models here.

from django.db import models
from apps.accounts.models import EducationalInstitute, User
from polymorphic.models import PolymorphicModel


class ActionTypes(models.TextChoices):
    Male = 'Male'
    Female = 'Female'


class Action(PolymorphicModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=ActionTypes.choices)

    def __str__(self):
        return self.name


class AttributeTypes(models.TextChoices):
    See = 'Male'
    Female = 'Female'


class Attribute(PolymorphicModel):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=10, choices=ActionTypes.choices)

    def __str__(self):
        return self.name


class RequiredBalance(Attribute):
    pass


class Cost(Attribute):
    pass


class Reward(Attribute):
    pass
