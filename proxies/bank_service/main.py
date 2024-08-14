from django.conf import settings
# from utilities.singleton_class import Singleton
import requests
import json

class Currency:
    name: str


class Money:
    currency: Currency
    value: float


class BankProxy():
    url = settings.BANK_URL + "/graphql"

    def create_session_party(self):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "query": "mutation { createParty(name: \""+f"{self.website}"+"\") { name coins { name description } } }"
        }
        response = requests.post(self.url, headers=headers, data=json.dumps(data))

        print(response.json())
    def __init__(self, website: str) -> None:
        self.website = website
        self.create_session_party()

    def meke_currencies(self , name , description):
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "query": "mutation { createCoin(partyName: \"" + f"{self.website}"+"\", name: \""+f"{name}"+"\", description: \""+f"{description}"+"\") { name coins { name description } } }"
        }

        response = requests.post(self.url, headers=headers, data=json.dumps(data))

        print(response.json())

    def get_currencies(self) -> list[Currency]:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "query": "query { getParty(name: \""+f"{self.website}"+"\") { name coins { name description } } }"
        }
        response = requests.post(self.url, headers=headers, data=json.dumps(data))

        print(response.json())
        return  response.json()

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





