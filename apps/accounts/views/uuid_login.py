import uuid
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils.user_management import create_or_get_user, find_user_in_website
from apps.accounts.views.base_login import BaseLoginView


import uuid
from rest_framework import status
from rest_framework.response import Response

from proxies.Shad import get_user_data_from_shad, update_user_info_by_shad_data

import logging
logger = logging.getLogger(__file__)


class UserIDLoginView(BaseLoginView):
    user_data_field = 'username'

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
            return Response({"error": "Invalid UserID. Must be a valid UUID."}, status=status.HTTP_400_BAD_REQUEST)

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
        website = request.website

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
                user.origin = origin
                user.save()
            response_status = status.HTTP_201_CREATED

        try:
            landing_id = request.data.get('landing_id')
            logger.info(
                f'landing_id: {landing_id} + user identifier: {user_identifier}')
            user_data = get_user_data_from_shad(
                user_uuid=user_identifier,
                landing_id=landing_id,
            )
            logger.info(
                f'user data: {str(user_data)}')
            update_user_info_by_shad_data(user, user_data)
        except ValueError as e:
            raise Exception(f'Cant get data from Shad. Error: {e}')

        self.create_login_event(user, website)
        return self.generate_response(user, created, response_status)
