from datetime import UTC, datetime, timedelta

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import DiscountCode, Merchandise, User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class MerchandiseFactory(DjangoModelFactory):
    class Meta:
        model = Merchandise


class DiscountCodeFactory(DjangoModelFactory):
    class Meta:
        model = DiscountCode

    code = factory.Faker("bothify", text="DISC#####")
    value = factory.Faker("pyfloat", min_value=0.05, max_value=0.5)
    expiration_date = factory.LazyFunction(
        lambda: datetime.now(UTC) + timedelta(days=30)
    )
    user = factory.SubFactory(UserFactory)
    discount_code_limit = factory.Faker("random_int", min=1000, max=50000)
