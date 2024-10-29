from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import UserWebsiteLogin
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.serializers.custom_token_obtain import CustomTokenObtainSerializer
from apps.accounts.utils import can_user_login, find_user_in_website
from errors.error_codes import serialize_error


class SimpleLogin(TokenObtainPairView):
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

        token_serializer = self.get_serializer(
            data={"username": user.username})

        token_serializer.is_valid(raise_exception=True)
        UserWebsiteLogin.objects.create(
            **{"user_website": user.get_user_website(website=website)})
        return Response({'user': UserSerializer(user).data, **token_serializer.validated_data},
                        status=status.HTTP_200_OK)
