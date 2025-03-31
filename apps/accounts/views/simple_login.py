from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ParseError
from django.db import transaction

from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils.user_management import find_user_in_website, can_user_login
from apps.accounts.views.base_login import BaseLoginView
from errors.error_codes import serialize_error


class SimpleLogin(BaseLoginView):
    user_identifier = 'username'  # Adjust based on your user model's identifier field
    # Field used to extract user identifier from request data
    user_data_field = 'username'

    @swagger_auto_schema(
        tags=['accounts'],
        responses={
            200: UserSerializer,
            400: "error code 4007 for not enough credentials",
            401: "error code 4006 for not submitted users & 4009 for wrong credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        return self.handle_post(request, *args, **kwargs)

    def get_user_identifier(self, request):
        # Extracts the user identifier (e.g., username/email) from request data
        return request.data.get(self.user_data_field)

    @transaction.atomic
    def handle_post(self, request):
        website = request.website
        user_data = request.data

        # Find user or raise exception if not found
        user = find_user_in_website(
            user_data=user_data,
            website=website,
            raise_exception=True
        )

        # Validate password presence
        password = user_data.get('password')
        if not password:
            raise ParseError(serialize_error('4007'))

        # Check if user can login with provided credentials
        if not can_user_login(user=user, password=password, website=website):
            raise ParseError(serialize_error('4009'))

        # Record login event
        self.create_login_event(user, website)

        # Generate HTTP response with tokens in cookies
        return self.generate_response(user, created=False, response_status=status.HTTP_200_OK)
