# documentation: https://github.com/kavenegar/kavenegar-python

from django.conf import settings
from kavenegar import *

from kamva_backend.settings.base import get_environment_var
from proxies.sms_system.main import SMSServiceProxy


class KaveNegarSMSServiceProxy(SMSServiceProxy):

    def __init__(self) -> None:
        super().__init__()
        self.kavenegar_api = KavenegarAPI(settings.KAVENEGAR_TOKEN)

    def send_sms(self):
        pass

    def send_otp(self, receptor_phone_number, action, token, token2=None, token3=None):
        template = None
        if action == 'verify-registration':
            template = 'verify'
        elif action == 'verify-changing-password':
            template = 'changePass'
        elif action == 'announce-changing-registration-status':
            template = 'announce-changing-registration-status'
        params = {
            'receptor': receptor_phone_number,
            'template': template,
            'token': token,
            'type': 'sms'
        }
        if token2:
            params['token2'] = token2
        if token3:
            params['token3'] = token3
        self.kavenegar_api.verify_lookup(params)
