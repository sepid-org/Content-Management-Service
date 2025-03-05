import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from content_management_service.authentication.safe_auth import SafeTokenAuthentication

logger = logging.getLogger(__file__)


class CheckAuthenticationView(APIView):
    authentication_classes = [SafeTokenAuthentication]

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({'status': 'unauthenticated'})

            return Response({'status': 'authenticated'})

        except Exception as e:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
