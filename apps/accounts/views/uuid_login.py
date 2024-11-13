import uuid
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.views.base_login import BaseLoginView


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

        # Check if user_id is provided
        if not user_id:
            return Response({"error": "UserID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate if user_id is a valid UUID
        if not self.is_valid_uuid(user_id):
            return Response({"error": "Invalid UserID format. Must be a valid UUID."}, status=status.HTTP_400_BAD_REQUEST)

        return self.handle_post(request)

    def get_user_identifier(self, request):
        return request.data.get("user_id")

    def is_valid_uuid(self, value):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False
