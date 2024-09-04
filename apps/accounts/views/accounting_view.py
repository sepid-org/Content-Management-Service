from rest_framework.decorators import api_view
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import UserWebsiteLogin, VerificationCode, User
from apps.accounts.permissions import IsHimself
from apps.accounts.serializers.user_serializer import PhoneNumberSerializer, PhoneNumberVerificationCodeSerializer, UserSerializer
from apps.accounts.serializers.custom_token_obtain import CustomTokenObtainSerializer
from apps.accounts.utils import can_user_login, create_or_get_user, find_user, find_user_in_website
from errors.error_codes import serialize_error
from errors.exceptions import ServiceUnavailable
from proxies.instant_messaging_service.main import InstantMessagingServiceProxy


class SendVerificationCode(GenericAPIView):
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
            party_display_name = serializer.validated_data.get(
                'party_display_name', 'سپید')
            verification_code = VerificationCode.objects.create_verification_code(
                phone_number=phone_number)
            try:
                verification_code.notify(
                    verification_type=serializer.validated_data.get(
                        'code_type', None),
                    party_display_name=party_display_name,
                )
            except:
                raise ServiceUnavailable(serialize_error('5000'))
            return Response({'detail': 'Verification code sent successfully'}, status=status.HTTP_200_OK)


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

        user = create_or_get_user(user_data=request.data,
                                  website=request.headers.get("Website"))

        token_serializer = CustomTokenObtainSerializer(
            data={'username': user.username})
        if token_serializer.is_valid(raise_exception=True):
            return Response({'account': UserSerializer(user).data, **token_serializer.validated_data},
                            status=status.HTTP_201_CREATED)


@api_view(["POST"])
def change_phone_number(request):
    # validate phone number with verification code:
    serializer = PhoneNumberVerificationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_phone_number = serializer.validated_data.get('phone_number', None)

    if find_user(user_data={'phone_number': new_phone_number}):
        raise ParseError(serialize_error('6002'))
    user = request.user
    user.phone_number = new_phone_number
    user.save()
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(tags=['accounts'],
                         responses={201: UserSerializer,
                                    400: "error code 4007 for not enough credentials",
                                    401: "error code 4006 for not submitted users & 4009 for wrong credentials"})
    def post(self, request, *args, **kwargs):
        website = request.headers.get("Website")
        user = find_user_in_website(
            user_data=request.data,
            website=website,
            raise_exception=True,
        )

        if not can_user_login(user=user, password=request.data.get("password"), website=website):
            raise ParseError(serialize_error('4009'))

        # todo: EHSAN
        # send greeting notification (just for testing)
        notification_service_proxy = InstantMessagingServiceProxy(website=website)
        notification_service_proxy.send_greeting_notification(recipient=user)


        token_serializer = self.get_serializer(
            data={"username": user.username})

        token_serializer.is_valid(raise_exception=True)
        UserWebsiteLogin.objects.create(
            **{"user_website": user.get_user_website(website=website)})
        return Response({'account': UserSerializer(user).data, **token_serializer.validated_data},
                        status=status.HTTP_200_OK)


class ChangePassword(GenericAPIView):
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

        user = find_user_in_website(
            user_data={"phone_number": phone_number},
            website=request.headers.get("Website"),
            raise_exception=True,
        )

        new_password = request.data.get("password")
        user.get_user_website(website=request.data.get(
            "website")).set_password(new_password=new_password)

        return Response(status=status.HTTP_200_OK)
