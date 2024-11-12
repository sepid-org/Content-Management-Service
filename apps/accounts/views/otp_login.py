from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError

from apps.accounts.models import UserWebsiteLogin, VerificationCode
from apps.accounts.serializers.user_serializer import PhoneNumberVerificationCodeSerializer, UserSerializer
from apps.accounts.utils import create_or_get_user, find_user_in_website, generate_tokens_for_user
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
        # Validate the verification code using the serializer
        verification_serializer = PhoneNumberVerificationCodeSerializer(
            data=request.data)
        verification_serializer.is_valid(raise_exception=True)

        phone_number = verification_serializer.validated_data['phone_number']
        website = request.headers.get("Website")

        # Try to find an existing user
        try:
            user = find_user_in_website(
                user_data={"phone_number": phone_number},
                website=website,
                raise_exception=True
            )
            created = False
            response_status = status.HTTP_200_OK
        except:
            # If user doesn't exist, create a new user and set an unusable password
            user_data = {
                'phone_number': phone_number,
                'username': phone_number,
            }

            user, created = create_or_get_user(
                user_data, website=request.headers.get("Website"))

            if created:
                user.set_unusable_password()
                user.save()
            response_status = status.HTTP_201_CREATED

        # Invalidate the verification code
        verification_code = VerificationCode.objects.get(
            phone_number=phone_number,
            code=verification_serializer.validated_data['code'],
            is_valid=True
        )
        verification_code.is_valid = False
        verification_code.save()

        # Create a login object to record user logins
        UserWebsiteLogin.objects.create(
            user_website=user.get_user_website(website=website)
        )

        # Generate tokens
        access_token, refresh_token = generate_tokens_for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(access_token),
            'refresh': str(refresh_token),
            'is_new_user': response_status == status.HTTP_201_CREATED
        }, status=response_status)
