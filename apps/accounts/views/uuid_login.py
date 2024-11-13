import uuid
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils import create_or_get_user, find_user_in_website
from apps.accounts.views.base_login import BaseLoginView


import uuid
from rest_framework import status
from rest_framework.response import Response


class UserIDLoginView(BaseLoginView):
    user_data_field = 'id'

    @swagger_auto_schema(
        tags=['accounts'],
        responses={
            200: UserSerializer,
            201: UserSerializer,
            400: "Error if UserID is invalid or missing, or if not a valid UUID"
        }
    )
    def post(self, request):
        user_id = request.data.get("user_id")
        origin = request.data.get("origin", "")

        # Check if user_id is provided
        if not user_id:
            return Response({"error": "UserID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate if user_id is a valid UUID
        if not self.is_valid_uuid(user_id):
            return Response({"error": "Invalid UserID format. Must be a valid UUID."}, status=status.HTTP_400_BAD_REQUEST)

        # Pass the origin to handle_post
        return self.handle_post(request, origin=origin)

    def get_user_identifier(self, request):
        return request.data.get("user_id")

    def is_valid_uuid(self, value):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    @transaction.atomic
    def handle_post(self, request, origin=""):
        user_identifier = self.get_user_identifier(request)
        website = request.headers.get("Website")

        try:
            user = find_user_in_website(
                user_data={self.user_data_field: user_identifier},
                website=website,
                raise_exception=True
            )
            created = False
            response_status = status.HTTP_200_OK
        except:
            user_data = self.get_user_data(user_identifier)
            user, created = create_or_get_user(user_data, website=website)

            if created:
                user.set_unusable_password()
                user.origin = origin  # Save origin for new users
                user.save()
            response_status = status.HTTP_201_CREATED

        # Update origin for existing users
        if not created and origin:
            user.origin = origin
            user.save(update_fields=["origin"])

        self.create_login_event(user, website)
        return self.generate_response(user, created, response_status)
