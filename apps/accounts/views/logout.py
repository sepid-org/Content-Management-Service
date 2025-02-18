from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []     # Disable permission checks

    def post(self, request):
        response = Response({"detail": "Successfully logged out"}, status=200)

        # پاک کردن کوکی‌ها
        response.delete_cookie(
            key='access_token',
            samesite='None',
            domain=settings.COOKIE_DOMAIN,
            path='/'
        )
        response.delete_cookie(
            key='refresh_token',
            samesite='None',
            domain=settings.COOKIE_DOMAIN,
            path='/'
        )

        # باطل کردن توکن ریفرش (اختیاری)
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                pass

        return response
