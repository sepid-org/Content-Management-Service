from django.conf import settings
from utilities.singleton_class import Singleton


class Currency:
    name: str


class Money:
    currency: Currency
    value: float


class BankProxy(Singleton):
    url = settings.BANK_URL

    def create_session(self):
        # todo: Ehsan
        pass

    def __init__(self, website: str) -> None:
        self.website = website
        self.create_session()

    def get_currencies(self) -> list[Currency]:
        # return website currencies
        # todo: Ehsan
        pass

    def deposit(self, user, money: Money):
        # todo: Ehsan
        pass

    def balance_inquiry(self, balance: list[Money]):
        # todo: Ehsan
        pass

    def withdraw(self, user, money: Money):
        # todo: Ehsan
        pass

    def transfer(self, sender, receiver, money: Money):
        pass
