from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

from apps.accounts.models import VerificationCode
from apps.accounts.serializers.user_serializer import PhoneNumberVerificationCodeSerializer, UserSerializer

from apps.accounts.utils import find_user_in_website, generate_secure_password, generate_tokens_for_user
from errors.error_codes import serialize_error


class OTPLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        tags=['accounts'],
        request_body=PhoneNumberVerificationCodeSerializer,
        responses={
            200: UserSerializer,
            201: UserSerializer,  # For new user creation
            400: "error code 4002 for len(code) < 5, 4003 for invalid & 4005 for expired code",
        }
    )
    @transaction.atomic
    def post(self, request):
        # First validate the verification code using your existing serializer
        verification_serializer = PhoneNumberVerificationCodeSerializer(
            data=request.data)
        verification_serializer.is_valid(raise_exception=True)

        phone_number = verification_serializer.validated_data['phone_number']
        website = request.headers.get("Website")

        # Try to find existing user
        try:
            user = find_user_in_website(
                user_data={"phone_number": phone_number},
                website=website,
                raise_exception=True
            )
            response_status = status.HTTP_200_OK
        except:
            # If user doesn't exist, create one with provided details
            user_data = {
                'phone_number': phone_number,
                'username': phone_number,
                'password': generate_secure_password(),
            }

            # Use your UserSerializer to create new user
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.create(user_serializer.validated_data)
            response_status = status.HTTP_201_CREATED

        # Generate tokens
        access_token, refresh_token = generate_tokens_for_user(user)

        # Invalidate the verification code
        verification_code = VerificationCode.objects.get(
            phone_number=phone_number,
            code=verification_serializer.validated_data['code'],
            is_valid=True
        )
        verification_code.is_valid = False
        verification_code.save()

        return Response({
            'user': UserSerializer(user).data,
            'access': str(access_token),
            'refresh': str(refresh_token),
            'is_new_user': response_status == status.HTTP_201_CREATED
        }, status=response_status)
