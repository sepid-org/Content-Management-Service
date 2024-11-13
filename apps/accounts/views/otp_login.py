from drf_yasg.utils import swagger_auto_schema

from apps.accounts.models import VerificationCode
from apps.accounts.serializers.user_serializer import UserSerializer, PhoneNumberVerificationCodeSerializer
from apps.accounts.views.base_login import BaseLoginView


class OTPLoginView(BaseLoginView):
    user_data_field = 'phone_number'

    @swagger_auto_schema(
        tags=['accounts'],
        request_body=PhoneNumberVerificationCodeSerializer,
        responses={
            200: UserSerializer,
            201: UserSerializer,
            400: "error code 4002 for len(code) < 5, 4003 for invalid & 4005 for expired code",
        }
    )
    def post(self, request):
        verification_serializer = PhoneNumberVerificationCodeSerializer(
            data=request.data)
        verification_serializer.is_valid(raise_exception=True)

        # Invalidate the verification code after successful validation
        phone_number = verification_serializer.validated_data['phone_number']
        VerificationCode.objects.filter(
            phone_number=phone_number,
            code=verification_serializer.validated_data['code'],
            is_valid=True
        ).update(is_valid=False)

        return self.handle_post(request)

    def get_user_identifier(self, request):
        return request.data.get("phone_number")
