from typing import Dict
from django.conf import settings
from utilities.singleton_class import Singleton
import requests
import json


class Currency:
    name: str
    display_name: str
    logo: str
    description: str


class Money:
    Dict[str, int]


class BankProxy(Singleton):
    url = settings.BANK_URL + "graphql"

    def create_session_party(self):
        data = {
            "query": "mutation { createParty(name: \""+f"{self.website}"+"\") { name coins { name description } } }"
        }
        self._post(data=data)

    def __init__(self, website: str) -> None:
        self.website = website
        self.create_session_party()

    def create_currency(self, name, display_name, logo, description) -> None:
        data = {
            "query": "mutation { createCoin(partyName: \"" + f"{self.website}"+"\", name: \""+f"{name}"+"\", description: \""+f"{description}"+"\") { name coins { name description } } }"
        }
        self._post(data=data)

    def get_currencies(self) -> list[Currency]:
        data = {
            "query": "query { getParty(name: \""+f"{self.website}"+"\") { name coins { name description } } }"
        }
        return self._post(data=data)

    def get_balance(self, user):
        # todo: Ehsan
        pass

    def deposit(self, user, money: Money):
        # todo: Ehsan
        pass

    def balance_inquiry(self, balance: list[Money]) -> bool:
        # todo: Ehsan
        pass

    def withdraw(self, user, money: Money):
        # todo: Ehsan
        pass

    def transfer(self, sender, receiver, money: Money):
        pass

    def _post(self, data):
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(
            self.url, headers=headers, data=json.dumps(data))
        return response.json()
