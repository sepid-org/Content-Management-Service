import requests

from manage_content_service.settings.base import get_environment_var
from utils.singleton_class import Singleton

url = get_environment_var(
    'EMAIL_SERVICE_URL', 'https://smtp.sepid.org/')


class EmailServiceProxy(Singleton):
    def __init__(self, website):
        self.website = website
        self.email = []
        self.subject = None
        self.body = {}
        # template types are: 'greeting', 'news', 'verification'
        self.template = None

    def _send(self):
        data = {
            'email': self.email,
            'subject': self.subject,
            'body': self.body,
            'template': self.template
        }
        res = requests.post(f'{url}send-email/', json=data)
        return res.status_code

    def send_verification_email(self, email: str, code: str, subject='تایید ایمیل'):
        self.email = [email]
        self.subject = subject
        self.body = {'code': code}
        self.template = 'verification'
        self._send()

    def send_news_email(self, email: list, news: str, subject='اطلاعیه جدید'):
        self.email = email
        self.subject = subject
        self.body = {'news': news}
        self.template = 'news'
        self._send()

    def send_greeting_email(self, email: str, name: str):
        self.email = [email]
        # todo: fetch website name from MWS
        website_name = 'کاموا'
        subject = f'به آکادمی {website_name} خوش آمدید!',
        self.subject = subject
        self.body = {'name': name}
        self.template = 'greeting'
        print(self._send())
