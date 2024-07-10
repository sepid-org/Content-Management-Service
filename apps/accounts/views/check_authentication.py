from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class CheckAuthenticationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # If the request reaches here, the token is valid
        return Response({'detail': 'Authentication token is valid.'}, status=status.HTTP_200_OK)
