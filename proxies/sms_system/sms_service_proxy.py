from proxies.sms_system.sms_service_interface import SMSService


class SMSServiceProxy(SMSService):
    provider: SMSService = None

    def __init__(self, provider: str) -> None:
        if provider == 'kavenegar':
            from proxies.sms_system.kavenegar import KaveNegarSMSService
            from django.conf import settings
            self.provider = KaveNegarSMSService(token=settings.KAVENEGAR_TOKEN)

    def send_otp(self, receptor_phone_number, action, token, token2=None, token3=None):
        self.provider.send_otp(receptor_phone_number,
                               action, token, token2, token3)

    def send_sms(self):
        self.provider.send_sms()

    def send_bulk(self):
        self.provider.send_bulk()
