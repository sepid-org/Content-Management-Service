from datetime import UTC, datetime, timedelta

import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import DiscountCode, Merchandise, User
from apps.fsm.models.program import Program


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program


class MerchandiseFactory(DjangoModelFactory):
    class Meta:
        model = Merchandise

    name = factory.Faker("name")
    price = factory.Faker("random_int", min=1000, max=50000)
    discounted_price = factory.Faker("random_int", min=500, max=1000)
    program = factory.SubFactory(ProgramFactory)


class DiscountCodeFactory(DjangoModelFactory):
    class Meta:
        model = DiscountCode

    code = factory.Faker("bothify", text="DISC###")
    value = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
    expiration_date = factory.LazyFunction(
        lambda: datetime.now(UTC) + timedelta(days=30)
    )
    user = factory.SubFactory(UserFactory)
    max_discount_amount = factory.Faker("random_int", min=1000, max=50000)
