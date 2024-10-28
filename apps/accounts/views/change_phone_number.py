from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.accounts.serializers.user_serializer import PhoneNumberVerificationCodeSerializer
from apps.accounts.utils import find_user
from errors.error_codes import serialize_error


@api_view(["POST"])
def change_phone_number_view(request):
    # validate phone number with verification code:
    serializer = PhoneNumberVerificationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_phone_number = serializer.validated_data.get('phone_number', None)

    if find_user(user_data={'phone_number': new_phone_number}):
        raise ParseError(serialize_error('6002'))
    user = request.user
    user.phone_number = new_phone_number
    user.save()
    return Response()
