import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__file__)


class CheckAuthenticationView(APIView):

    def get(self, request):
        try:
            logger.warning("111", request.user, request.user.is_authenticated)
            if not request.user.is_authenticated:
                return Response({'status': 'unauthenticated'})

            logger.warning("222", request.user)
            return Response({'status': 'authenticated'})

        except Exception as e:
            logger.warning("333", e)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
