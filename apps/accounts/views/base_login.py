from django.db import transaction
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.models import UserWebsiteLogin
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils.user_management import create_or_get_user, find_user_in_website, generate_tokens_for_user


class BaseLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    user_identifier = None  # Should be set by subclasses
    user_data_field = None  # e.g., 'id' or 'phone_number'
    response_serializer = UserSerializer

    def get_user_identifier(self, request):
        raise NotImplementedError("Subclasses should implement this method.")

    def get_user_data(self, user_identifier):
        return {self.user_data_field: user_identifier, 'username': user_identifier, 'is_temporary': True}

    def create_login_event(self, user, website):
        UserWebsiteLogin.objects.create(
            user_website=user.get_user_website(website=website)
        )

    def generate_response(self, user, created, response_status):
        access_token, refresh_token = generate_tokens_for_user(user)
        return Response({
            'user': self.response_serializer(user).data,
            'access': str(access_token),
            'refresh': str(refresh_token),
            'is_new_user': created
        }, status=response_status)

    @transaction.atomic
    def handle_post(self, request):
        user_identifier = self.get_user_identifier(request)
        website = request.website

        try:
            user = find_user_in_website(
                user_data={self.user_data_field: user_identifier},
                website=website,
                raise_exception=True
            )
            created = False
            response_status = status.HTTP_200_OK
        except Exception as e:
            user_data = self.get_user_data(user_identifier)
            user, created = create_or_get_user(user_data, website=website)
            response_status = status.HTTP_201_CREATED

        self.create_login_event(user, website)
        return self.generate_response(user, created, response_status)
