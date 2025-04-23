from django.conf import settings
import requests
from utils.singleton_class import Singleton


class InstantMessagingServiceProxy(Singleton):
    url = settings.IMS_URL

    def __init__(self, website):
        self.website = website

    def send_solve_question_reward_notification(self, recipient_id, question_id, cost):
        message = f'بابت حل سوال {question_id} به شما {cost} امتیاز اضافه شد'
        self._send_notification(recipient_id=recipient_id, message=message)

    def send_submit_answer_cost_notification(self, recipient_id, question_id, cost):
        message = f'بابت اقدام به حل سوال {question_id} {cost} قدر پول از شما کم شد'
        self._send_notification(recipient_id=recipient_id, message=message)

    def send_greeting_notification(self, recipient_id):
        message = 'به آکادمی خود خوش آمدید!'
        self._send_notification(recipient_id=recipient_id, message=message)

    def _send_notification(self, recipient_id, message):
        res = requests.post(
            f'{self.url}/send-message', json={'sender': self.website, 'recipient': str(recipient_id), 'message': message})
        return res.status_code
