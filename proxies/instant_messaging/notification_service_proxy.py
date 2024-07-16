import requests
from manage_content_service.settings.base import get_environment_var
from utilities.singleton_class import Singleton

url = get_environment_var(
    'INSTANT_MESSAGE_URL', 'https://ims.sepid.org/')


class NotificationServiceProxy(Singleton):
    def __init__(self, website: str):
        self.sender = website

    def send_notification(self, receiver, message):
        res = requests.post(
            f'{url}/send-message', json={'sender': self.sender, 'receiver': receiver, 'message': message})
        return res.status_code
