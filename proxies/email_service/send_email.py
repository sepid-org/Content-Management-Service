import requests


class Email_Service_collector():
    def __init__(self , email:[] ,subject:None , body:{}):
        self.email = email
        self.subject = subject
        self.body = body

    def sender(self):
        data = {'email': self.email, 'subject': self.subject, "body": self.body}
        res = requests.post('http://127.0.0.1:8080/send-email/', json=data)
        return res.status_code
