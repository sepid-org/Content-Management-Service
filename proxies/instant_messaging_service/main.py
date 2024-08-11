from django.conf import settings
import requests
from utilities.singleton_class import Singleton


class InstantMessagingServiceProxy(Singleton):
    url = settings.INSTANT_MESSAGE_URL

    def __init__(self, website):
        self.website = website

    def send_notification(self, recipient, message):
        res = requests.post(
            f'{self.url}/send-message', json={'sender': self.website, 'recipient': recipient, 'message': message})
        return res.status_code
