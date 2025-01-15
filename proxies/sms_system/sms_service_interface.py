from abc import ABC, abstractmethod


class SMSService(ABC):

    class OtpTypes:
        CreateUserAccount = 'create-user-account'
        ChangeUserPassword = 'change-user-password'
        ChangeUserPhoneNumber = 'change-user-phone-number'

    class RegularSMSTypes:
        UpdateRegistrationReceiptState = 'update-registration-receipt-state'

    @abstractmethod
    def send_otp(self, receptor_phone_number, action, token, token2=None, token3=None):
        pass

    @abstractmethod
    def send_sms(self):
        pass

    @abstractmethod
    def send_bulk(self):
        pass


class VoiceCallService(ABC):

    @abstractmethod
    def make_voice_call(self):
        pass
