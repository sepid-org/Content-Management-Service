from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import User, UserWebsiteLogin
from apps.accounts.permissions import IsHimself
from apps.accounts.serializers.user_serializer import PhoneNumberVerificationCodeSerializer, UserSerializer
from apps.accounts.utils.user_management import create_or_get_user, find_user_in_website, generate_tokens_for_user
from errors.error_codes import serialize_error


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializer_action_classes = {
        'create': PhoneNumberVerificationCodeSerializer
    }
    my_tags = ['accounts']

    def get_parser_classes(self):
        if self.action == 'create':
            return ()
        else:
            return (MultiPartParser,)

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsHimself]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return User.objects.none()
        elif user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=user.id)

    @swagger_auto_schema(responses={201: UserSerializer,
                                    400: "error code 4002 for len(code) < 5, 4003 for invalid code, "
                                         "4004 for previously submitted users & 4005 for expired code",
                                    })
    @transaction.atomic
    def create(self, request):
        # validate phone number with verification code:
        serializer = PhoneNumberVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = find_user_in_website(user_data=request.data,
                                    website=request.headers.get("Website"))
        if user:
            raise ParseError(serialize_error('4117'))

        user, _ = create_or_get_user(user_data=request.data,
                                     website=request.headers.get("Website"))

        website = request.headers.get("Website")

        # create a login object to save users logins
        UserWebsiteLogin.objects.create(
            user_website=user.get_user_website(website=website)
        )

        access_token, refresh_token = generate_tokens_for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(access_token),
            'refresh': str(refresh_token),
        }, status=status.HTTP_201_CREATED)
