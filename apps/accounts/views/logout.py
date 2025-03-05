from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permission checks

    def post(self, request):
        try:
            # Expecting the refresh token to be sent in the request data
            refresh_token = request.data.get("refresh")

            if refresh_token is None:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            # Blacklist the refresh token so it can no longer be used
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            # In case the token is invalid or any error occurs
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
