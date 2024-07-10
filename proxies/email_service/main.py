import requests

from manage_content_service.settings.base import get_environment_var

url = get_environment_var(
    'EMAIL_SERVICE_URL', 'https://smtp.sepid.org/')


class EmailServiceProxy():
    # todo: set email template type alongside the subject and email properties, not in the body
    def __init__(self):
        self.email = []
        self.subject = None
        self.body = {}

    def _send(self):
        data = {'email': [self.email],
                'subject': self.subject, "body": self.body}
        res = requests.post(url, json=data)
        return res.status_code

    def send_verification_email(self, email, code: str, subject='تایید ایمیل'):
        self.email = email
        self.subject = subject
        self.body = {"code": code, "type": 2}
        self._send()

    def send_news_email(self, email, news: str, subject='اطلاعیه جدید'):
        self.email = email
        self.subject = subject
        self.body = {"news": news, "type": 3}
        self._send()

    def send_greeting_email(self, email, name: str, subject='خوش آمدید!'):
        self.email = email
        self.subject = subject
        self.body = {"name": name, "type": 1}
        print(self._send())
