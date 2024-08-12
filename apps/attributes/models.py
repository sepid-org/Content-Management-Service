from django.db import models

# Create your models here.

from django.db import models
from apps.accounts.models import EducationalInstitute, User
from polymorphic.models import PolymorphicModel


class Attribute(PolymorphicModel):
    name = models.CharField(max_length=50, unique=True)
    value = models.JSONField(default=dict)

    def __str__(self):
        return self.name

    def apply():
        pass


class RequiredBalance(Attribute):
    pass


class Cost(Attribute):
    pass


class Reward(Attribute):
    pass
