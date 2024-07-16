import requests

# from manage_content_service.settings.base import get_environment_var
#
# url = get_environment_var(
#     'INSTANT_MESSAGE_URL', 'https://ims.sepid.org/')
#
url = 'https://ims.sepid.org'

class NotifServiceProxy():
    def __init__(self ,website):
        self.website= website
        self.notif = None


    def send_notification(self, reciver , message):
        self.notif = message
        res = requests.post(f'{url}/send-message', json={'sender':self.website , 'reciver':reciver , 'message':self.notif})
        return res.status_code



