import requests
from manage_content_service.settings.base import get_environment_var
from utilities.singleton_class import Singleton

url = get_environment_var(
    'INSTANT_MESSAGE_URL', 'https://ims.sepid.org/')


class InstantMessagingServiceProxy(Singleton):
    def __init__(self, website):
        self.website = website

    def send_notification(self, recipient, message):
        res = requests.post(
            f'{url}/send-message', json={'sender': self.website, 'recipient': recipient, 'message': message})
        return res.status_code
