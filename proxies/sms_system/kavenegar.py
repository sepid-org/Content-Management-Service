# documentation: https://github.com/kavenegar/kavenegar-python

from kavenegar import *

from proxies.sms_system.main import SMSServiceProxy


class KaveNegarSMSServiceProxy(SMSServiceProxy):

    def __init__(self, token) -> None:
        super().__init__()
        self.api = KavenegarAPI(token)

    def send_sms(self):
        pass

    def send_otp(self, receptor_phone_number, type, token, token2=None, token3=None):
        params = {
            'receptor': receptor_phone_number,
            'template': type,
            'token': token,
            'type': 'sms'
        }
        if token2:
            params['token2'] = token2
        if token3:
            params['token3'] = token3
        self.api.verify_lookup(params)
