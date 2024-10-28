from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accounts.models import VerificationCode
from apps.accounts.serializers.user_serializer import PhoneNumberSerializer
from errors.error_codes import serialize_error
from errors.exceptions import ServiceUnavailable


class VerificationCodeView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PhoneNumberSerializer
    my_tags = ['accounts']

    @swagger_auto_schema(operation_description="Sends verification code to verify phone number or change password",
                         responses={200: "Verification code sent successfully",
                                    400: "error code 4000 for not being digits & 4001 for phone length less than 10",
                                    404: "error code 4008 for not finding user to change password",
                                    500: "error code 5000 for problems in sending SMS",
                                    })
    @transaction.atomic
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone_number = serializer.validated_data.get('phone_number', None)
            website_display_name = serializer.validated_data.get(
                'website_display_name', 'سپید')
            verification_code = VerificationCode.objects.create_verification_code(
                phone_number=phone_number)
            try:
                verification_code.notify(
                    verification_type=serializer.validated_data.get(
                        'code_type', None),
                    website_display_name=website_display_name,
                )
            except:
                raise ServiceUnavailable(serialize_error('5000'))
            return Response({'detail': 'Verification code sent successfully'}, status=status.HTTP_200_OK)
