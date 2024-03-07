SMS_CODE_DELAY = 5

SMS_CODE_LENGTH = 5


def get_sms_service_proxy(type, token):
    if type == 'kavenegar':
        from proxies.sms_system.kavenegar import KaveNegarSMSServiceProxy
        # todo: get token from backend
        from django.conf import settings
        return KaveNegarSMSServiceProxy(token=settings.KAVENEGAR_TOKEN)


class SMSServiceProxy:
    class OtpTypes:
        CreateUserAccount = 'create-user-account'
        ChangeUserPassword = 'change-user-password'
        ChangeUserPhoneNumber = 'change-user-phone-number'

    class RegularSMSTypes:
        UpdateRegistrationReceiptState = 'update-registration-receipt-state'

    def send_otp(self, receptor_phone_number, action, token, token2=None, token3=None):
        pass

    def send_sms():
        pass

    def send_bulk():
        pass


class VoiceCallServiceProxy:
    def make_voice_call():
        pass
