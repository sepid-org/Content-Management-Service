import requests

from manage_content_service.settings.base import get_environment_var
from utilities.singleton_class import Singleton

url = get_environment_var(
    'EMAIL_SERVICE_URL', 'https://smtp.sepid.org/')


class EmailServiceProxy(Singleton):
    # todo: set email template type alongside the subject and email properties, not in the body
    def __init__(self):
        self.email = []
        self.subject = None
        self.body = {}

    def _send(self):
        data = {'email': self.email, 'subject': self.subject, "body": self.body}
        res = requests.post(f'{url}send-email/', json=data)
        return res.status_code

    def send_verification_email(self, email: str, code: str, subject='تایید ایمیل'):
        self.email = [email]
        self.subject = subject
        self.body = {"code": code, "type": 2}
        self._send()

    def send_news_email(self, email: list, news: str, subject='اطلاعیه جدید'):
        self.email = email
        self.subject = subject
        self.body = {"news": news, "type": 3}
        self._send()

    def send_greeting_email(self, email: str, name: str, subject='خوش آمدید!'):
        self.email = [email]
        self.subject = subject
        self.body = {"name": name, "type": 1}
        print(self._send())
