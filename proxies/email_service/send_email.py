import requests


class EmailServiceCollector():
    def __init__(self, email: [], subject: None, body: {}):
        self.email = email
        self.subject = subject
        self.body = body

    def _send(self):
        data = {'email': self.email, 'subject': self.subject, "body": self.body}
        res = requests.post('http://127.0.0.1:8080/send-email/', json=data)
        return res.status_code

    def send_verification_email(self, code: None):
        self.body = {"code": code, "type": 2}
        self._send()

    def send_news_email(self, news: None):
        self.body = {"news": news, "type": 3}
        self._send()

    def send_greeting_email(self, name: None):
        self.body = {"name": name, "type": 1}
        self._send()
