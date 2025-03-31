from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.accounts.serializers.user_serializer import PhoneNumberVerificationCodeSerializer, UserSerializer
from apps.accounts.utils.user_management import find_user_in_website


class ChangePasswordView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PhoneNumberVerificationCodeSerializer

    @swagger_auto_schema(tags=['accounts'],
                         responses={200: UserSerializer,
                                    400: "error code 4002 for len(code) < 5, 4003 for invalid & 4005 for expired code",
                                    })
    @transaction.atomic
    def post(self, request):
        serializer = PhoneNumberVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get('phone_number', None)
        website = request.website

        user = find_user_in_website(
            user_data={"phone_number": phone_number},
            website=website,
            raise_exception=True,
        )

        user.get_user_website(website=website)\
            .set_password(new_password=request.data.get("password"))

        return Response(status=status.HTTP_200_OK)
