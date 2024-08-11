from django.conf import settings
from utilities.singleton_class import Singleton


class BankProxy(Singleton):
    url = settings.BANK_URL

    def create_session(self):
        # todo
        pass

    def __init__(self, website) -> None:
        self.website = website
        self.create_session()

    def deposit(self, user, currency, value):
        self.transfer(
            sender=self.website,
            receiver=user,
            currency=currency,
            value=value
        )

    def withdraw(self, user, currency, value):
        self.transfer(
            sender=user,
            receiver=self.website,
            currency=currency,
            value=value
        )

    def transfer(self, sender, receiver, value):
        pass
