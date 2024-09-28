from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404

from apps.accounts.models import User
from apps.accounts.serializers.user_serializer import UserPublicInfoSerializer


class UserListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Get list of UUIDs from the request data
        user_ids = request.data.get('user_ids', [])

        if not user_ids:
            return Response({"detail": "No user_ids provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve users matching the UUIDs
            users = get_list_or_404(User, id__in=user_ids)
            serializer = UserPublicInfoSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            # Handle the case where invalid UUIDs are provided
            return Response({"detail": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
